Is Applicable
===

"is-applicable.py" is a script that gets a list of Fixlet and Task IDs, and a site name and determines whether or not the content is applicable to a set of computers.

The script lists on the console, for each fixlet and task, the names of all computers it is applicable to.

Parameters
---

 * `-f, --fixlets`           Specify a list of fixlet IDs to read, seperated by comma(,); if a file named "content.txt" is detected, will read the file to get the list. 
 * `-t, --tasks`             Specify a list of task IDs to read, seperated by comma(,);
 * `-sn, --sitename`         Specify the name of site containing the fixlets or tasks, within double quotes.


Usage
---

python is-applicable.py -u [USERNAME] -p [PASSWORD] -s [SERVER[:PORT]] -sn [SITE NAME] -f ["fixlet1,fixlet2..."] -t ["task1,task2..."] 

