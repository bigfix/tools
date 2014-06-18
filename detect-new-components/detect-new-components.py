import datetime
from time import strftime, gmtime
import sys
import os
import pickle

from bs4 import BeautifulSoup
import requests

from argparse import ArgumentParser
from getpass import getpass
import json


class BigFixArgParser(ArgumentParser):
  name = "Usage: detect-new-components.py [options]"
  base_usage = """Options:
  -h, --help                    Print this help message and exit
  -s, --server SERVER[:PORT]    REST API server and port
  -u, --user                    REST API user
  -p, --password                REST API password
  -k, --insecure                Don't verify the HTTPS Connection to the server

  Optional arguments:
  -c, --cacheFile cacheFile     
            Name a file to cache components that are detected already
            (default: priorComponents.dict)
  -o, --outputProperties "id" "operting system" ...
            properties of new [bes computer] to output
            (default: "agent version" "name" "ip address")
  -i, --identifyProperties "cpu" "id" "operating system" ...
            properties of [bes computer] whose change indicate a new component
            (default: "cpu" "id" "operating system")
  -m, --misc_relevance "relevance statement" 
            Bool relevance expression to filter which new components to output
            (default: "true")
            (example: "operating system of it contains Win")
  """

  def __init__(self):
    description = "Detects new components that has joined the environment since last run"

    super(BigFixArgParser, self).__init__(add_help=False,
      usage=self.base_usage, description=description)

    self.add_argument('-u', '--user', required=True)
    self.add_argument('-p', '--password', required=False)
    self.add_argument('-s', '--server', required=True)
    self.add_argument('-k', '--insecure', action='store_true')

    #optional arguments:
    self.add_argument('-c', '--cacheFile', required=False, nargs='?', 
      default="priorComponents.dict", const="priorComponents.dict")
    self.add_argument('-o', '--outputProperties', required=False, nargs='*', 
      default=["agent version","name","ip address"])
    self.add_argument('-i', '--identifyProperties', required=False, nargs='*', 
      default=["cpu", "id", "operating system"])
    self.add_argument('-m', '--misc_relevance', required=False, nargs='?', 
      default="true", const="true")

    self.tool_usage = None
    self.password = None

  def parse_args(self):
    combined_usage = self.base_usage
    if self.tool_usage is not None:
      combined_usage += "\n" + self.tool_usage

    self.usage = "{0}\n\n{1}\n\n{2}".format(self.name,
      self.description, combined_usage)

    if '-h' in sys.argv or '--help' in sys.argv:
      print(self.usage)
      sys.exit()

    args = super(BigFixArgParser, self).parse_args()

    if not args.password:
      prompt = "Enter password for user '{0}': ".format(args.user)
      args.password = getpass(prompt)

    if ':' not in args.server:
      args.server = args.server + ':52311'

    return args

def checkNotInCache(identifiersList):
  identifier = "".join(identifiersList)
  if identifier in db['seenComputers']:
    return False
  else:
    db['seenComputers'].add(identifier)
    return True


defaultDB = {  
  "updateDate":strftime("%d %b %Y %H:%M:%S GMT", gmtime(0)),
  "seenComputers":set() 
}

db = defaultDB

def main():
  global db

  """ Parse the args """
  args = BigFixArgParser().parse_args()

  """ Database Setup """
  if (os.access(args.cacheFile, os.F_OK) \
      and not os.access(args.cacheFile, os.R_OK | os.W_OK)):
    #Cache exists, but RW is forbidden
    print "Error: Access to cache file", args.cacheFile, "blocked. Exiting"
    sys.exit(1);
  elif os.access(args.cacheFile, os.F_OK): 
    #Cache exists and is readable.
    try:
      db = pickle.load(open(args.cacheFile, 'r+'))
    except Exception:
      print "Error: Cache format corrupted. Exiting"
      sys.exit(1);
  else:
    #cache does not exist.
    db = defaultDB;

  """ Construct a query string """
  #along the lines of: 
  #'(id of it, name of it, [property] of it...) 
  # of (bes computers whose (evaluating relevance) )'
  requestProperties = args.outputProperties + args.identifyProperties
  out = [prop + " of it" for prop in requestProperties] 
  outStr = "("+  ", ".join(out) + ")"    #--> "(id of it, name of it)"
  q = outStr \
      +' of (bes computers whose (last report time of it > "'
      +db['updateDate']+'" as time and '+args.misc_relevance+') )'

  """ Query the Server """
  res = requests.get(
    url   ="https://"+args.server+"/api/query/?relevance="+q, 
    auth  =(args.user, args.password),
    verify=not args.insecure)
  db['updateDate'] = strftime("%d %b %Y %H:%M:%S GMT", gmtime())
  #update the last checked date.

  """ Analyze Response """
  soup = BeautifulSoup(res.text)
  n_out = len(args.outputProperties)

  for resultTuple in soup.findAll('tuple'):
    result = [x.string for x in resultTuple.findAll('answer')]

    """ Foreach machine: Filter with Cache """
    if checkNotInCache(result[n_out:]):
      print "\t".join(result[:n_out])

  """ Dump Cache back to disk """
  pickle.dump(db, open(args.cacheFile, 'w+'), protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
  main()