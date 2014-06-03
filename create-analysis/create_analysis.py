from sys import stdin, stdout
import sys
import datetime
import time
import re
from BeautifulSoup import BeautifulSoup as bs
from argparse import ArgumentParser
from getpass import getpass
import requests



""" The command line argument parser """
class BigFixArgParser(ArgumentParser):
  name = "Usage: create_analysis.py [options]"
  base_usage = """Options:
  -a, --analysis_name         Analysis name
  -d, --description           Analysis description
  -h, --help                  Print this help message and exit
  -s, --server SERVER[:PORT]  REST API server and port
  -u, --user                  REST API user
  -p, --password              REST API password
  -t, --site_type             Site type: master/custom/operator/external
  -n, --site_name             Site-name
  -k, --insecure              Ignore SSL verification

  Note:
    This application takes the relevance from stdin, each query statement should be in one line"""

  def __init__(self):
    description = "A tool for creating a smarter planet"

    super(BigFixArgParser, self).__init__(add_help=False,
      usage=self.base_usage, description=description)

    self.add_argument('-u', '--user', required=True)
    self.add_argument('-p', '--password', required=True)
    self.add_argument('-s', '--server', required=True)
    self.add_argument('-t', '--site_type', required=True)
    self.add_argument('-n', '--site_name', required=True)
    self.add_argument('-a', '--analysis_name', required=True)
    self.add_argument('-d', '--description', required=True)
    self.add_argument('-k', '--insecure', action='store_true')
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

    if ':' not in args.server:
      args.server = args.server + ':52311'

    return args



""" Compose analysis with template
    param:
      name: the name of the analysis, in string format
      description: the description of the analysis, in string format
      relevance: a list of relevance queries, each of which is a string
    return:
      the composed XML analysis as a string """
def compose_analysis(name, description, relevance):
  time = str(datetime.datetime.now())[:10]

  analysis = """<?xml version="1.0" encoding="UTF-8"?>
<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BES.xsd">
<Analysis>
<Title>{0}</Title>
<Description>{1}</Description>
<Relevance>true</Relevance>
<Source>Internal</Source>
<SourceReleaseDate>{2}</SourceReleaseDate>
<Domain>BESC</Domain>\n""".format(name, description, time)
  count = 1
  for line in relevance:
      analysis += '<Property Name="Analysis {0}" ID="{0}">{1}</Property>\n'.format(str(count), line)
      count += 1
  analysis += """</Analysis>\n</BES>"""
  return analysis



""" Create the analysis on server
  param:
    server: server address and port as a string, should be "server:port"
    site_type: a string indicating the type of site, should be one of [master, external, operator, custom]
    user: username as string
    password: password as string
    analysis: composed XML document of analysis
    insecure: boolean value indicating whether to use insecure connection
  return:
    the text response from server """
def create_analysis(server, site_type, site_name, user, password, analysis, insecure):
  if site_type == "master":
    site = "https://{0}/api/analyses/{1}".format(server, site_type)
  else:
    site = "https://{0}/api/analyses/{1}/{2}".format(server, site_type, site_name)
  r = requests.post(site, auth=(user, password), data=analysis, verify=not insecure)
  return r.text


""" Find the ID string in a server reply, if no ID is found, print notice and exit
  param:
    reply: the server reply text, in string format
  return:
    the ID string """
def find_id(reply):
  found = re.findall(r'<ID>[0-9]*?</ID>', reply)
  if len(found) == 0:
    print "Analysis creation failed!"
    exit(1)
  return found[0][4: len(found[0]) - 5]


""" Print the analysis evaluation result
  param:
    ID: the ID number of analysis, in string format
    server: server address and port as a string, should be "server:port"
    user: username as string
    password: password as string
    insecure: boolean value indicating whether to use insecure connection
    query_length: Integer value of the number of statements in the analysis input
  return:
    None """
def print_result(ID, server, user, password, insecure, query_length):
  computers = requests.post('https://{0}/api/query'.format(server), auth=(user, password), verify=not insecure,
                        data={'relevance': '(it as string) of properties whose (it as string contains "bes computers")'}
                        ).text
  computer_num = len(re.findall(r'string">([^>]*?)<', computers))
  while True:
    result = requests.post('https://{0}/api/query'.format(server), auth=(user, password), verify=not insecure,
                        data={'relevance': '(name of computer of it, value of it) of results of bes properties whose (item 1 of id of it = ({0}))'.format(ID)}
                        ).text
    result = re.findall(r'string">([^>]*?)<', result)
    if len(result) / 2 == computer_num * query_length:
      print "Report collected!\n\n"
      count = 0
      while count < len(result):
        print "Computer name:  " + result[count]
        print "     Result:  " + result[count + 1] + "\n"
        count += 2
      break
    print "Waiting for report, got {0} / {1}".format(len(result) / 2, computer_num * query_length)
    time.sleep(10)




def main():
  """ Parse the args """
  args = BigFixArgParser().parse_args()
  """ Read the relevance from stdin and filter out empty lines """
  relevance = stdin.read().splitlines()
  relevance = filter(lambda s: s.strip() != '', relevance)
  """ Compose the analysis XML """
  analysis = compose_analysis(args.analysis_name, args.description, relevance)
  """ Create the analysis on server, get reply """
  reply = create_analysis(args.server, args.site_type, args.site_name,
                          args.user, args.password, analysis, args.insecure)
  """ Search for ID in the reply """
  ID = find_id(reply)
  """ Get analysis evaluation result """
  print_result(ID, args.server, args.user, args.password, args.insecure, len(relevance))




if __name__ == "__main__":
  main()

