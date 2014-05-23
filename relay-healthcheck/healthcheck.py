from bs4 import BeautifulSoup
import base64
import urllib
import sys
from urlparse import urlparse
import requests
import json
import argparse
import getpass

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("--username")
	parser.add_argument("--server")
	if len(sys.argv) == 1:
	    parser.print_help()
	    sys.exit(1)
	args = parser.parse_args()
	serv = args.server
	username = args.username
	password = getpass.getpass("password:")
	authHeader = createSession(username, password)
	healthChecks = loadHealthChecks()
	evaluateHealthChecks(serv, authHeader, healthChecks)

def loadHealthChecks():
	jsonchecks = open("healthchecks.json")
	checkdata = json.load(jsonchecks)
	jsonchecks.close()
	return checkdata

def createSession(username, password):
	s = requests.Session()
	base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
	return  "Basic %s" % base64string

def request(url, relDict, authHeader):
	try:
	    r = requests.get(url, 
	            headers={'Authorization': authHeader},
	            verify=False,
	            params = relDict)
	    if r.status_code != 200:
	    	sys.stderr.write("Error: Received bad response from server. Code: " + str(r.status_code))
	    	sys.exit(1)
	    return r
	except requests.exceptions.ConnectionError:
		sys.stderr.write("Could not connect to REST api.")
		sys.exit(1)

def fetchStatusResult(serv, rel, authHeader):
	res = request('https://' + serv + ':52311/api/query', {'relevance': rel} ,authHeader).text
	resBS = BeautifulSoup(res)
	passFailAnswer = None
	passFailAnswer = resBS.query.result.answer.text
	resstatus = formatStatus(passFailAnswer)
	return resstatus

def formatStatus(ans):
	if ans == "True":
		return "Failed"
	elif ans == "False":
		return "Passed"
	else:
		return ans

def evaluateHealthChecks(serv, authHeader, healthChecks):
	passCount = 0
	totalCount = 0
	for section in healthChecks["HealthCheckSections"]:
		print "++" + section["SectionName"] + "++"
		for check in section["checklist"]:
			status = fetchStatusResult(serv, check["checkrel"], authHeader)
			print "\t" + status.upper() + "\t\t" + check["name"] + " - " + check["severity"] 
			if status == "Passed":
				passCount += 1
			totalCount += 1
	print "\nHealth Check Complete"
	print "Checks Passed:" + str(passCount) + "/" + str(totalCount)

if __name__ == "__main__":
    main()