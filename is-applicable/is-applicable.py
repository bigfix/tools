#!/usr/bin/env python

import os
import sys
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join("../example")))
import example
import requests

def read():
	parser = example.BigFixArgParser()
	parser.add_argument('-f', '--fixlets', required = False, help = 'List of fixlets to read in')
	parser.add_argument('-t', '--tasks', required = False, help = 'List of tasks to read in')
	parser.add_argument('-sn', '--sitename', required = True, help = 'Name of site containing content')
	parser.base_usage += """
  -f, --fixlets               Specify a list of fixlet IDs to read, seperated by comma(,); if a file named "content.txt" is detected, will read the file to get the list. 
  -t, --tasks                 Specify a list of task IDs to read, seperated by comma(,);
  -sn, --sitename             Specify the name of site containing the fixlets or tasks, within double quotes.
	"""
	parser.description = 'Used to determine applicability of content'
	args_fixlets = ""
	args_tasks = ""
	args = parser.parse_args()
	
	site = args.sitename
	args_fixlets = args.fixlets
	args_tasks = args.tasks
	
	if (args.fixlets == None and args_tasks == None):
		print "Input must contain a fixlet or a task."
		quit()
	else: 
		content_list = args_fixlets + "," + args_tasks
		content_list = content_list.split(",")

		apply_relevance(content_list, args, site)
		#apply_relevance(fixlets_list, tasks_list, args, site)

def apply_relevance(content_list, args, site):
	query1 = 'names%20of%20bes%20computers%20whose%20%28relevants%20%28%20%28fixlets%20of%20bes%20site%20whose%20%28name%20of%20it%20is%20"'
	query2 = '"%29%29%20whose%20%28id%20of%20it%20is%20'
	query3 = '%29%29%20of%20it%29'
	
	for f in content_list:
		computers = requests.get('https://'+args.server+'/api/query/?relevance='+query1+site+query2+f+query3, auth = (args.user, args.password), verify = not args.insecure)
		soup = BeautifulSoup(computers.text)
		answers = soup.find_all('answer')
		output = "Fixlet/Task ID: " + f + "     Relevant computers(" + str(len(answers)) + "): "
		for ans in answers:
			output = output + ans.string + ' '
		print output
	
if __name__=='__main__':
    read()
	
	
	
	
	
	
	


	









