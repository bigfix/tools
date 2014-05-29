from bs4 import BeautifulSoup
import base64
import urllib
import sys, os
from urlparse import urlparse
import requests
import json
import argparse
import getpass

# Allow relative import of BigFixArgParser
sys.path.append(os.path.abspath(os.path.join("../example")))
from example import BigFixArgParser

def main():
    args = BigFixArgParser().parse_args()
    auth = requests.auth.HTTPBasicAuth(args.user, args.password);
    health_checks = load_health_checks()
    evaluate_health_checks(args.server, auth, health_checks)

def load_health_checks():
    json_checks = open("healthchecks.json")
    check_data = json.load(json_checks)
    json_checks.close()
    return check_data

def make_request(url, relevance, auth):
    try:
        r = requests.get(url,
                auth=auth,
                verify=False,
                params = relevance)
        if r.status_code != 200:
            sys.stderr.write("Error: Bad response from server. Code: " +
                             str(r.status_code))
            sys.exit(1)
        return r
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Could not connect to REST api.")
        sys.exit(1)

def fetch_status_result(serv, relevance, authHeader):
    res = make_request("https://" + serv + "/api/query",
                       {"relevance": relevance} ,authHeader).text
    resBS = BeautifulSoup(res)
    if resBS.query.result.answer is None:
        resstatus = format_status("False")	
    else:
        resstatus = format_status(resBS.query.result.answer.text)
    return resstatus

def format_status(ans):
    if ans == "True":
        return "Failed"
    elif ans == "False":
        return "Passed"
    else:
        return ans

def evaluate_health_checks(serv, auth, healthChecks):
    fetch_status_result(serv, "0", auth)
    passCount = 0
    totalCount = 0
    for section in healthChecks["HealthCheckSections"]:
        print "++" + section["SectionName"] + "++"
        for check in section["checklist"]:
            status = fetch_status_result(serv, check["checkrel"], auth)
            print ("\t" + status.upper() + "\t\t" + check["name"] +
                   " - " + check["severity"]) 
            if status == "Passed":
                passCount += 1
            totalCount += 1
    print "\nHealth Check Complete"
    print "Checks Passed:" + str(passCount) + "/" + str(totalCount)

if __name__ == "__main__":
    main()
