#!/usr/bin/env python

import sys
from argparse import ArgumentParser
from getpass import getpass

class BigFixArgParser(ArgumentParser):
  name = "hodor.py [options]"

  def __init__(self):
    description = "A tool for creating a smarter planet"
    usage = """Options:
  -h, --help                  Print this help message and exit
  -s, --server SERVER[:PORT]  REST API server and port
  -u, --user USER[:PASSWORD]  REST API user and password
  -k, --insecure              Don't verify the HTTPS connection to the server
  -c, --cacert FILE           CA certificate used to verify the server's HTTPS
                              certificate"""

    super(BigFixArgParser, self).__init__(add_help=False,
      usage=usage, description=description)

    self.add_argument('-k', '--insecure', action='store_true')
    self.add_argument('-c', '--cacert')
    self.add_argument('-u', '--user', required=True)
    self.add_argument('-s', '--server', required=True)

  def parse_args(self):
    self.usage = "{0}\n\n{1}\n\n{2}".format(self.name,
      self.description, self.usage)

    if '-h' in sys.argv or '--help' in sys.argv:
      print(self.usage)
      sys.exit()

    args = super(BigFixArgParser, self).parse_args()

    if ':' not in args.user:
      prompt = "Enter password for user '{0}': ".format(args.user)
      args.user = args.user + ':' + getpass(prompt)

    return args

parser = BigFixArgParser()
print(parser.parse_args())
