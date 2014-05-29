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

	auth = tuple(s for s in user.split(':'))
	r = requests.get(server+'api/sites',
		auth = auth,
		verify = args.insecure,
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

	r = requests.get( server+'api/fixlets/%s/%s'% \
		(source_site[1], source_site[0]), # /type/name
		auth = auth,
		verify = args.insecure )
	r = BeautifulSoup(r.text)

	fixlets = []
	for fixlet in r.find_all('fixlet'):
		fixlets.append( (fixlet.find('name').text, fixlet['resource']) )

	total_kib_copied = 0
	for fixlet_name, fixlet_url in fixlets:
		print "Copying", fixlet_name
		r = requests.get( fixlet_url,
			auth = auth,
			verify = args.insecure )
		postr = requests.post( server+'api/fixlets/%s/%s'% \
			(destination_site[1], destination_site[0]), # /type/name
			data = r.content,
			auth = auth,
			verify = args.insecure )
		print sys.getsizeof(r.content) / 1024.0, "KiB copied"
		total_kib_copied += sys.getsizeof(r.content) / 1024.0
	print total_kib_copied, "KiB in total copied"


def wrong():
	externalURLrelevance = \
		"(name of it, urls of it) of BES sites whose (external site flag of it)"

	# grab external site URLs
	r = requests.get(server+'api/query?relevance=%s'%externalURLrelevance,
		auth = auth,
		verify = False,
		params = None)

	if r.status_code != 200:
		# not OKAY, do something
		pass

	siteURLs = []
	r = BeautifulSoup(r.text)
	for site in r.find_all('tuple'):
		site = site.find_all('answer')
		print site[0].text + site[1].text
		siteURLs.append(site[1].text)

	for externalsite in siteURLs:
		r = requests.get(externalsite)
		if r.status_code != 200:
			# no OKAY, do something
			pass

		# nested MIME multiparts
		# outer is content + sig
		# inner is content: listing of files
		mimemsg = email.message_from_string(r.text)
		if not mimemsg.is_multipart():
			# not the expected structure, do something
			pass
		# look through content
		innermimemsg = mimemsg.get_payload(0)
		count = 0
		resourceURLs = []
		for item in innermimemsg.get_payload():
			item_s = str(item)

			itemtype = item_s[item_s.find('TYPE: ')+6 : \
				item_s.find('\n',item_s.find('TYPE: '))].strip()
			url = item_s[item_s.find('URL: ')+5 : \
				item_s.find('\n',item_s.find('URL: '))].strip()

			if itemtype != "NONCLIENTFILE":
				resourceURLs.append(url)
				count += 1

		print "Found %s files"%count

		for resourceURL in resourceURLs:
			print resourceURL
			r = requests.get(resourceURL)
			resourceMIME = email.message_from_string(r.text.encode('utf-8'))


if __name__ == "__main__":
	main()
