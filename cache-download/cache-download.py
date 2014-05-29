#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.abspath(os.path.join("../example")))

import bs4
import example
import re
import requests
import urllib

GIGABYTE = 1024*1024*1024
FETCH_ALL_GATHER_QUERY = '(name of it, urls of it) of bes sites whose (external site flag of it)'
FIXLET_REGEXP = '(http://.*\.fxf)'
PREFETCH_REGEXP = 'prefetch\s+(\S+)\s+(sha1:\S+)\s+(size:\d+)\s+(\S+)\s+(sha256:\S+)?'
CACHE_LOCATION = '/var/opt/BESServer/wwwrootbes/bfmirror/downloads/sha1/'
# CACHE_LOCATION = ''
# TODO location of file cache is /var/opt/BESServer/besserver.config

args = {}
session = None
username = ''
password = ''
secure = True

def run():
    global args, session, username, password, secure
    # set up argument parsing
    parser = example.BigFixArgParser()
    parser.description = 'A script to pre-fetch downloads to a root server'
    parser.base_usage += """
  -v, --verbose               Print more output
  -n, --dry-run               Only print names of files to cache
  -x, --sites [SITES]         Specify a list of sites to prefetch downloads from
  -m, --maxsize [SIZE]        Avoids caching files with sizes larger than SIZE in bytes
  -d, --name [REGEX]          Specify a regular expression of filenames to prefetch for
  -r, --url [REGEX]           Specify a regular expression of URLs to look at"""
    parser.add_argument('-x', '--sites', default = None, nargs = '*', help='a list of sites to pre-fetch downloads from (default is any site)')
    parser.add_argument('-m', '--maxsize', default = GIGABYTE, help='avoid caching files larger than some size, in bytes (default is 1GB)')
    parser.add_argument('-d', '--name', help='only download files whose names contain some regular expression')
    parser.add_argument('-r', '--url', help='only download files whose urls contain some regular expression')
    args = parser.parse_args()

    user_str = args.user.split(':')
    username, password = args.user.split(':')
    secure = not args.insecure

    session = requests.Session()
    print args

    c = 0

    already_prefetched = set()
    gathers = fetch_gather_urls()
    for site in gathers:
        fixlet_urls = fetch_fixlet_urls(gathers[site])
        for url in fixlet_urls:
            prefetch_actions = fetch_fixlet_prefetch_actions(url.group())
            for prefetch_action in prefetch_actions:
                filename, sha1, size, download, sha256 = prefetch_action.groups()
                sha1 = sha1[5:]
                sha256 = sha256[7:] if not sha256 is None else None
                size = int(size[5:])

                if size > args.maxsize:
                    continue

                if sha1 in already_prefetched:
                    continue
                else:
                    already_prefetched.add(sha1)

                target = CACHE_LOCATION + sha1
                print 'downloading {}...'.format(download)
                # urllib.urlretrieve(download, target)
                print 'saved file {} [{}] to {}'.format(filename, size, target)
                c = c + 1
                if c == 5:
                    return

def fetch_fixlet_prefetch_actions(url):
    response = requests.get(url, auth=(username, password), verify=secure)
    return re.finditer(PREFETCH_REGEXP, response.text)

def fetch_fixlet_urls(url):
    response = requests.get(url, auth=(username, password), verify=secure)
    return re.finditer(FIXLET_REGEXP, response.text)

def fetch_gather_urls():
    '''Use a relevance query to fetch all gather urls'''
    url = 'https://' + args.server + '/api/query?relevance=' + FETCH_ALL_GATHER_QUERY
    response = requests.get(url, auth=(username, password), verify=secure)
    parsed = bs4.BeautifulSoup(response.text)
    pairs = parsed.result.find_all('tuple')
    pairs = [p.find_all('answer') for p in pairs]
    pairs = [(p[0].string, p[1].string) for p in pairs]
    return dict(pairs)

if __name__=='__main__':
    run()
