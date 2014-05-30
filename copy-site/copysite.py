# copysite.py
#
# Copy resources from one site (e.g. external) to another (e.g. internal)
# Parses through Fixlets, Tasks, Analyses and copies them using the API

from bs4 import BeautifulSoup
import requests
import mimetypes
import email
from email.parser import Parser
import re
import sys, os
import hashlib

# from example.example import BigFixArgParser
sys.path.append(os.path.abspath(os.path.join("../example")))
from example import BigFixArgParser


def scrub_fixlet(fixlet):
	"""Takes a fixlet xml as a string and removes the timestamp tag
	so that the same fixlet will have the same hash regardless of date
	last accessed"""
	cut = 'x-fixlet-modification-time</Name>'
	cutstart = fixlet.index('<Value>', fixlet.find(cut))+7
	cutend = fixlet.index('</Value>', cutstart)
	return fixlet[:cutstart] + fixlet[cutend:]

def scrub_fixlet_hash(fixlet):
	"""Takes a fixlet xml as a string and replaces the timestamp tag
	with the md5 of the timestampless fixlet, so that I don't have to
	redownload all the fixlets to know their hashes to check for dupes

	Story time. There are PUT and POST endpts for updating fixlets, but
	using these API endpts modifies the last access timestamp (I think).
	So actually the best place to store the md5 is in the timestamp, 
	because if the fixlet is ever modified the md5 is deleted, as opposed
	to if I made a separate xml tag for md5. (I think)."""
	cut = 'x-fixlet-modification-time</Name>'
	cutstart = fixlet.index('<Value>', fixlet.find(cut))+7
	cutend = fixlet.index('</Value>', cutstart)
	return fixlet[:cutstart] + "md5: " + \
		hashlib.md5(fixlet[:cutstart] + fixlet[cutend:]).hexdigest() + \
		fixlet[cutend:]

def main():
	parser = BigFixArgParser()
	parser.tool_usage = """copysite options:
  -r, --source-site           Name of site to copy resources from
  -d, --destination-site      Name of site to copy resources to
  -t, --test                  Run tests to see if the script worked correctly

  Example use:
  python copysite.py -k -u user -p pass -s https://server:host/ -r "BES Support" -d target_site
	"""
	parser.add_argument('-r', '--source-site', required=True)
	parser.add_argument('-d', '--destination-site', required=True)
	parser.add_argument('-t', '--test', action='store_true')
	args = parser.parse_args()
	auth = (args.user, args.password)
	server = args.server
	secureSSL = not args.insecure
	testing = args.test

	# cleaner for the code
	# get = lambda url, **kwargs: \
	# 	requests(url, **kwargs, auth = auth, verify = secureSSL)
	def get(url, **kwargs):
		r = requests.get(url, auth = auth, verify = secureSSL, **kwargs)
		if r.status_code != 200:
			# kill execution
			raise requests.exceptions.RequestException("Error in GET request. %s for url %s"%(r, url))
		return r

	source_site = None # these will remain None if site not found
	destination_site = None

	# locate sites, find source and dest
	print "Checking to see if sites exist..."
	r = get(server+'api/sites')
	if r.status_code != 200:
		# not OKAY
		print "Error in sending request %s"%r
		return
	r = BeautifulSoup(r.text)
	for site in r.find_all(re.compile('\\w*site\\b')):
		site = (site.find('name').text.strip(), site.name[:-4], site['resource'])
		if site[0] == args.source_site:
			source_site = site
		elif site[0] == args.destination_site:
			destination_site = site
	if source_site is None or destination_site is None:
		print "Specified site(s) do not exist!"
		return

	if testing:
		test(auth, server, secureSSL, source_site, destination_site, get)
	else:
		copy_site(auth, server, secureSSL, source_site, destination_site, get)

def copy_site(auth, server, secureSSL, source_site, destination_site, get):
	"""Perform the actual copy of content (fixlets) from SRC
	to DEST sites"""

	# find fixlet candidates to copy
	print "Finding copy candidates from SOURCE."
	r = get( server+'api/fixlets/%s/%s'%(source_site[1], source_site[0]) )
	r = BeautifulSoup(r.text)

	fixlets = []
	for fixlet in r.find_all('fixlet'):
		fixlets.append( (fixlet.find('name').text, fixlet['resource'], 
			fixlet.id.text) )

	# find fixlets already on dest
	print "Enumerating existing fixlets on DEST."
	r = get( server+'api/fixlets/%s/%s'% \
		(destination_site[1], destination_site[0]))
	r = BeautifulSoup(r.text)

	dest_fixlets = []
	for fixlet in r.find_all('fixlet'):
		dest_fixlets.append( (fixlet.find('name').text, fixlet['resource'], 
			fixlet.id.text, fixlet.find('value', text='x-fixlet-modification-time')) )

	dest_fixlets_hash = dict() # a set of hashes.. lul cuz each fixlet is mem large
	for fixlet_name, fixlet_url, fixlet_id, fixlet_timestamp in dest_fixlets:
		if fixlet_timestamp[:5] == 'md5: ':
			print "Found fixlet that had hash."
			fixlet_hash = fixlet_timestamp[5:]
		else:
			r = get( fixlet_url )

			# fixlets timestamp themselves, so we'll cut that out to find dupes'
			content_scrubbed = scrub_fixlet(r.content)

			fixlet_hash = hashlib.md5(content_scrubbed).hexdigest()

		if fixlet_hash in dest_fixlets_hash:
			# found a duplicate, delete it
			print "Found duplicate fixlets on DEST: ID", fixlet_id, \
				"which duplicates", dest_fixlets_hash[fixlet_hash]
			print "Deleting duplicate..."
			deleter = requests.delete( fixlet_url,
				auth = auth,
				verify = secureSSL )
			if deleter.status_code != 200:
				print "Unable to delete fixlet", fixlet_id, "!!"
		else:
			dest_fixlets_hash[ fixlet_hash ] = fixlet_id


	# copy the new fixlets from src to dest
	print "Begin copying fixlets."
	total_kib_copied = 0
	for fixlet_name, fixlet_url, fixlet_id in fixlets:
		r = get( fixlet_url )

		content_scrubbed = scrub_fixlet(r.content)

		if hashlib.md5(content_scrubbed).hexdigest() in dest_fixlets_hash:
			# dest has this one already, skip it
			print "Found fixlet", fixlet_id, "from SOURCE already in DEST," \
				"skipping..."
			continue

		print "Copying", fixlet_id, ":", fixlet_name, repr(hashlib.md5(r.content).hexdigest())

		postr = requests.post( server+'api/fixlets/%s/%s'% \
			(destination_site[1], destination_site[0]), # /type/name
			data = scrub_fixlet_hash(r.content),
			auth = auth,
			verify = secureSSL )
		print sys.getsizeof(r.content) / 1024.0, "KiB copied"
		total_kib_copied += sys.getsizeof(r.content) / 1024.0
	print total_kib_copied, "KiB in total copied"

	# test(auth, server, secureSSL, get)


def test(auth, server, secureSSL, source_site, destination_site, get):
	# let's do some QA, a whole lot got copied and i have no idea if it worked
	def get_names(url):
		nameset = set()
		r = get(url)
		r = BeautifulSoup(r.content)
		for nametag in r.find_all('name'):
			nameset.add(nametag.text)
		return nameset

	dest_names = get_names(server+'api/fixlets/%s/%s'% \
		(destination_site[1], destination_site[0]))
	src_names = get_names(server+'api/fixlets/%s/%s'% \
		(source_site[1], source_site[0]))
	
	in_src_but_not_dest = src_names - dest_names
	if in_src_but_not_dest:
		print "Some items in SRC are not found in DEST!"
		print in_src_but_not_dest
	else:
		print "All %d items in SRC are found in DEST"%len(src_names)

if __name__ == "__main__":
	main()
