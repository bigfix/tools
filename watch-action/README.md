Watch Actions
===

"watch_actions.py" is a script that gets a list of actions and parses the corresponding ActionScripts to detect the existence of actions specified by the users. Under standard mode, the script will output the url and the actions detected. Under verbose mode, the script outputs the exact line of the action.

The action watched could be brief commands (i.e. delete, wait) and it could be specific actions with argument (i.e. delete __Local\Get\BESServerAPI.exe, continue if {"True" = parameter "ServerUpgradeResult"}, ).

Parameters
---

-a, --actions [ACTIONS/FILENAME]   Specify a list of actions to watch, seperated by comma(,); 
                                   if FILENAME with .wal extension detected, will read the file to get the list. 
-v, --verbose                      To see the full list of commands that contain watched actions.
-t, --time [MINUTE]                To change the waiting period between checks, default is 60.
    

Usage
---

python watch_action.py -u [USERNAME] -p [PASSWORD] -s [SERVER[:PORT]] -a ["action1,action2,..."/filename.wal] -t [MINUTE] -v

Other
---

The API for actions: https://www.ibm.com/developerworks/community/wikis/home?lang=en#!/wiki/Tivoli%20Endpoint%20Manager/page/BigFix%20Actions