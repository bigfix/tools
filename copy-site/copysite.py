# copysite.py
#
# Copy resources from one site (e.g. external) to another (e.g. internal)
# Parses through Fixlets, Tasks, Analyses and copies them using the API

from example.example import BigFixArgParser

from bs4 import BeautifulSoup
import requests
import mimetypes
import email
from email.parser import Parser
import re
import sys
import hashlib


def main():
	parser = BigFixArgParser()
	parser.tool_usage = """copysite options:
  -r, --source-site           Name of site to copy resources from
  -d, --destination-site      Name of site to copy resources to
	"""
	parser.add_argument('-r', '--source-site', required=True)
	parser.add_argument('-d', '--destination-site', required=True)
	args = parser.parse_args()
	user = args.user
	server = args.server
	insecure = args.insecure
	source_site = None # these will remain None if site not found
	destination_site = None

	# locate sites, find source and dest
	auth = tuple(s for s in user.split(':'))
	r = requests.get(server+'api/sites',
		auth = auth,
		verify = insecure,
		params = None)

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

	# find fixlet candidates to copy
	r = requests.get( server+'api/fixlets/%s/%s'% \
		(source_site[1], source_site[0]), # /type/name
		auth = auth,
		verify = insecure )
	r = BeautifulSoup(r.text)

	fixlets = []
	for fixlet in r.find_all('fixlet'):
		fixlets.append( (fixlet.find('name').text, fixlet['resource'], 
			fixlet.id.text) )

	# find fixlets already on dest
	r = requests.get( server+'api/fixlets/%s/%s'% \
		(destination_site[1], destination_site[0]), # /type/name
		auth = auth,
		verify = insecure)
	r = BeautifulSoup(r.text)

	dest_fixlets = []
	for fixlet in r.find_all('fixlet'):
		dest_fixlets.append( (fixlet.find('name').text, fixlet['resource'], 
			fixlet.id.text) )

	dest_fixlets_hash = dict() # a set of hashes.. lul cuz each fixlet is mem large
	for fixlet_name, fixlet_url, fixlet_id in dest_fixlets:
		r = requests.get( fixlet_url, 
			auth = auth,
			verify = insecure)

		fixlet_hash = hashlib.md5(r.content).hexdigest()
		if fixlet_hash in dest_fixlets_hash:
			# found a duplicate, delete it
			print "Found duplicate fixlet: ID", fixlet_id, \
				"duplicates", dest_fixlets_hash[fixlet_hash]
			print "Deleting duplicate..."
			deleter = requests.delete( fixlet_url,
				auth = auth,
				verify = insecure )
			if deleter.status_code != 200:
				print "Unable to delete fixlet", fixlet_id, "!!"
		else:
			dest_fixlets[ hashlib.md5(r.content).hexdigest() ] = 

	# copy the new fixlets from src to dest
	total_kib_copied = 0
	for fixlet_name, fixlet_url, fixlet_id in fixlets:
		print "Copying", fixlet_id, ":", fixlet_name
		r = requests.get( fixlet_url,
			auth = auth,
			verify = insecure )

		if hashlib.md5(r.content).hexdigest() in dest_fixlets:
			# dest has this one already, skip it
			continue

		postr = requests.post( server+'api/fixlets/%s/%s'% \
			(destination_site[1], destination_site[0]), # /type/name
			data = r.content,
			auth = auth,
			verify = insecure )
		print sys.getsizeof(r.content) / 1024.0, "KiB copied"
		total_kib_copied += sys.getsizeof(r.content) / 1024.0
	print total_kib_copied, "KiB in total copied"


if __name__ == "__main__":
	main()
