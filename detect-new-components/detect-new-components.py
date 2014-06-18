# (id of it, name of it) of (bes computers whose (last report time of it > "02 Jan 2014 04:06 GMT" as time) )
#(id of it, name of it, ip address of it, agent version of it) of (bes computers whose (last report time of it > "02 Jan 2014 04:06 GMT" as time) )
import datetime
from time import strftime, ctime
import sys
import os
import pickle

from bs4 import BeautifulSoup
import requests as re

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
  -c, --cacheFile cacheFile     Name a file to cache components that are detected already
                                (default: priorComponents.dict)
  -o, --outputProperties "id" "operting system" ...
                                properties of new [bes computer] to output
                                (default: "agent version" "computer name" "ip")
  -i, --identifyProperties "cpu" "id" "operating system" ...
                                properties of [bes computer] that indicate a new component when changed
                                (default: "cpu" "id" "operating system")
  -m, --misc_relevance "relevance statement" 
                                Boolean relevance statement to filter which new components to output
                                (default "true")
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
    self.add_argument('-c', '--cacheFile', required=False, nargs='?', default="priorComponents.dict", const="priorComponents.dict")
    self.add_argument('-o', '--outputProperties', required=False, nargs='*', default=["agent version","computer name","ip"])
    self.add_argument('-i', '--identifyProperties', required=False, nargs='*', default=["cpu", "id", "operating system"])
    self.add_argument('-m', '--misc_relevance', required=False, nargs='?', default="true", const="true")


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




def main():
  """ Parse the args """
  args = BigFixArgParser().parse_args()
  print args

  """ Housekeeping """
  if not os.access(args.cacheFile, os.F_OK)
    print "Creating cache:", args.cacheFile
    cfile = open(args.cacheFile, "r+")
    pickle.dump({
      "updateDate":strftime("%a, %d %b %Y %H:%M:%S +0000", ctime(0))
      "seenComputers":set() },
      cfile, 
      pickle.HIGHEST_PROTOCOL)
    cfile.close();

  if not os.access(args.cacheFile, os.R_OK | os.W_OK)
    print "Read/Write access to cache file", args.cacheFile, "blocked. Exiting"
    sys.exit(1)

  """ Construct a query string """




if __name__ == "__main__":
  main()

