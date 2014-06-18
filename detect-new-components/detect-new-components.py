# (id of it, name of it) of (bes computers whose (last report time of it > "02 Jan 2014 04:06 GMT" as time) )
#(id of it, name of it, ip address of it, agent version of it) of (bes computers whose (last report time of it > "02 Jan 2014 04:06 GMT" as time) )
import datetime
import sys

from bs4 import BeautifulSoup
import requests as re

from argparse import ArgumentParser
from getpass import getpass
import json


class BigFixArgParser(ArgumentParser):
  name = "Usage: detect-new-components.py [options]"
  base_usage = """Options:
  -h, --help                    Print this help message and exit
  -c, --config [config.json]    Use configuration file, default config.json
  -k, --insecure                See insecure param in cURL

  The following is also required if they are not present within config:
  -s, --server SERVER[:PORT]    REST API server and port
  -u, --user                    REST API user
  -p, --password                REST API password

"""

  def __init__(self):
    description = "Detects new components that has joined the environment since last run"

    super(BigFixArgParser, self).__init__(add_help=False,
      usage=self.base_usage, description=description)
    self.add_argument('-c', '--custom_config', required=True, action='store')
    self.add_argument('-k', '--insecure', action='store_true')

    self.add_argument('-u', '--user', required=False)
    self.add_argument('-p', '--password', required=False)
    self.add_argument('-s', '--server', required=False)
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
    print args
    cfile = open(args.custom_config)
    config = json.load(cfile)


    if not args.password and args.user:
      prompt = "Enter password for user '{0}': ".format(args.user)
      args.password = getpass(prompt)

    if ':' not in args.server:
      args.server = args.server + ':52311'

    return args




def main():
  """ Parse the args """
  args = BigFixArgParser().parse_args()
  print args


if __name__ == "__main__":
  main()

