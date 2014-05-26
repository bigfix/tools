#!/usr/bin/env python

import sys
from argparse import ArgumentParser
from getpass import getpass

class BigFixArgParser(ArgumentParser):
  name = "Usage: hodor.py [options]"
  base_usage = """Options:
  -h, --help                  Print this help message and exit
  -s, --server SERVER[:PORT]  REST API server and port
  -u, --user USER[:PASSWORD]  REST API user and password
  -k, --insecure              Don't verify the HTTPS connection to the server"""

  def __init__(self):
    description = "A tool for creating a smarter planet"

    super(BigFixArgParser, self).__init__(add_help=False,
      usage=self.base_usage, description=description)

    self.add_argument('-k', '--insecure', action='store_true')
    self.add_argument('-u', '--user', required=True)
    self.add_argument('-s', '--server', required=True)
    self.tool_usage = None

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

    if ':' not in args.user:
      prompt = "Enter password for user '{0}': ".format(args.user)
      args.user = args.user + ':' + getpass(prompt)

    return args
