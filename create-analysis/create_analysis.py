from sys import stdin, stdout
import sys
import datetime
import re
from BeautifulSoup import BeautifulSoup as bs
from argparse import ArgumentParser
from getpass import getpass
import requests




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
  -n, --site_name         Site-name

  Note:
    This application takes the relevance from stdin!"""

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



def compose_analysis(name, description, relevance):
  time = str(datetime.datetime.now())[:10]
  return """<?xml version="1.0" encoding="UTF-8"?>
  <BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BES.xsd">
    <Analysis>
      <Title>{0}</Title>
      <Description>{1}</Description>
      <Relevance>{2}</Relevance>
      <Source>Internal</Source>
      <SourceReleaseDate>{3}</SourceReleaseDate>
      <Domain>BESC</Domain>
      <Property Name="New Property" ID="1">exists BES computer</Property>
    </Analysis>
  </BES>
  """.format(name, description, relevance, time)




def create_analysis(server, site_type, site_name, user, password, analysis, insecure):
  if site_type == "master":
    site = "https://{0}/api/analyses/{1}".format(server, site_type)
  else:
    site = "https://{0}/api/analyses/{1}/{2}".format(server, site_type, site_name)
  r = requests.post(site, auth=(user, password), data=analysis, verify=not insecure)
  return r.text


def find_id(reply):
  found = re.findall(r'<ID>[0-9]*?</ID>', reply)
  if len(found) == 0:
    print "Analysis creation failed!"
    exit(1)
  return found[0][4: len(found[0]) - 5]

def print_result(ID, server, user, password, insecure):
  property_id = requests.post('https://{0}/api/query'.format(server), auth=(user, password), verify=not insecure,
                              data={'relevance': '(ids of it as string) of bes properties whose (item 1 of id of it = {0})'.format(ID)}
                             ).text
  property_id = re.findall(r'string">([0-9, ]*?)<', property_id)
  for line in property_id:
    result = requests.post('https://{0}/api/query'.format(server), auth=(user, password), verify=not insecure,
                        data={'relevance': '(name of computer of it, value of it) of results of bes properties whose (id of it = ({0}))'.format(line)}
                        ).text
    result = re.findall(r'string">([^>]*?)<', result)
    print "Computer name:  " + result[0]
    print "     Result:  " + result[1] + "\n"




def main():
  args = BigFixArgParser().parse_args()
  relevance = stdin.read().splitlines()
  analysis = compose_analysis(args.analysis_name, args.description, relevance)
  reply = create_analysis(args.server, args.site_type, args.site_name,
                          args.user, args.password, analysis, args.insecure)
  ID = find_id(reply)
  print_result(46, args.server, args.user, args.password, args.insecure)




if __name__ == "__main__":
  main()

