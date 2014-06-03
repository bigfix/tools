import os
import sys
sys.path.append(os.path.abspath(os.path.join("../example")))

import example
import requests
from lxml import etree
import re
import schedule
import time

def watch():
    # set up argument parsing
    parser = example.BigFixArgParser()
    parser.add_argument('-a', '--actions', required = False, help = 'List of actions to watch')
    parser.add_argument('-v', '--verbose', default = False, action = "store_true", required = False, help = 'To see the full list of commands that contain watched actions')
    parser.add_argument('-t', '--time', default = 60, required = False, help = 'To set the waiting period')
    parser.base_usage += """
  -a, --actions [ACTIONS/FILENAME]   Specify a list of actions to watch, seperated by comma(,); 
                                     if FILENAME with .wal extension detected, will read the file to get the list. 
  -v, --verbose                      To see the full list of commands that contain watched actions
  -t, --time [MINUTE]                   A number specifing the waiting period between checks"""
    
    parser.description = 'Used to watch certain actions'
    ext = ".wal"
    args = parser.parse_args()
    args_actions = ""
    if ext in args.actions:
        actions_file = open(args.actions, 'r')
        for line in actions_file:
                args_actions += line
    else:
        args_actions = args.actions
    actions_list = args_actions.split(",")

    watched_actions = gen_regex(actions_list)
    action_record = {}
    for a in actions_list:
        action_record[a] = False

    t = int(args.time)
    gen_summary(action_record, watched_actions, args)
    schedule.every(t).minutes.do(gen_summary, action_record, watched_actions, args)
    while True:
        schedule.run_pending()

def gen_summary(action_record, watched_actions, args):
    get_action = requests.get('https://'+args.server+'/api/actions', auth = (args.user, args.password), verify = not args.insecure)
    actions_content = etree.fromstring(get_action.content)
    resources = actions_content.xpath("/BESAPI/Action/@Resource")
    for url in resources:
        script_xml = requests.get(url, auth = (args.user, args.password), verify = not args.insecure)
        script_content = etree.fromstring(script_xml.content)
        script = script_content.xpath('/BES/SingleAction/ActionScript')[0].text
        commands = script.split("\n")
        local_record = dict(action_record)
        print("ActionScript URL: " + url)
        for c in commands:
            action_caught = watched_actions.match(c)
            if not action_caught == None:
                local_record[action_caught.group(0).strip()] = True
                if (args.verbose):
                    print("WARNING: " + c.strip())
        summary = "Summary: The ActionScript contains "
        safe = True
        for a in local_record:
            if local_record[a]:
                safe = False
                summary += a + "; "
        if safe:
            print "Summary: The ActionScript contains None of the watched actions."
        else:
            print summary

# reformat the list of actions into a regex ^\s*(action1|action2|...)
def gen_regex(actions_list):
    result = "^\s*("
    for a in actions_list:
        result += a.strip()+"|"
    result = result[:-1]
    result += ")"
    return re.compile(result)

if __name__=='__main__':
    watch()
