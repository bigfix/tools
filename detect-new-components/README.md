Detect new components that join the environment
  * Configurable to component
  * Output component version, computer name, IP address


# Usage

## Prerequisites
- [python-2.7](https://www.python.org/downloads/)
- BeautifulSoup `pip install beautifulsoup4`
- Requests `pip install requests`


## Parameters
```
-h, --help                    Print this help message and exit
-s, --server SERVER[:PORT]    REST API server and port
-u, --user                    REST API user
-p, --password                REST API password
-k, --insecure                Do not verify the HTTPS Connection to the server

Optional:
-c, --cacheFile cacheFile     
        Name a file to cache components that are detected already
        (default: priorComponents.dict)
-o, --outputProperties "id" "operting system" ...
        properties of new [bes computer] to output
        (default: "agent version" "name" "ip address")
-i, --identifyProperties "cpu" "id" "operating system" ...
        properties of [bes computer] whose change indicate a new component
        (default: "cpu" "id" "operating system")
-m, --misc_relevance "relevance statement" 
        Bool relevance expression to filter which new components to output
        (default: "true")
        (example: "operating system of it contains Win")
```

## Example
In this example, the admin queries the BigFix Server for the id and Computer Name of any new component that has joined the environment, or changed cpu/OS/device type since last run.

    python detect-new-components.py -s 9.12.148.24 -u admin -p password
    				-c prior_1.txt
    				-o "id" "name"
    				-i "cpu" "id" "unique value" "operating system" "device type"

And outputs the -o properties in a tab-delimited format.


## Discussion:
Concurrently, backend implementation is done through pickle-dumping a Set, and the Last Check Date. However, the following limitations exist and cause inefficiencies in the code.
 * In an idea world, there should be no need to make a separate cache of 'seen' components. Any newly-joined component should be flagged as 'new' by the Environment.
 * Just as there is no flag for a new component, or a 'first contact time' record, the current heuristic is to check out all the BES Computers that have reported back since the last time the program was run. This is an imperfect solution, but is better than polling all the computers.
 * The current implementation may not be scalable when the environment grows very large (in the millions), and has not been tested in such an environment.

 An explorable implementation is to have a relevance expression that will return True on machines that are new. Once you have used this relevance statement to identify 'new' components, you can then send another fixlet to them such that subsequent applications of the prior relevance expression will return False. This is a slower option, but yields higher accuracy.
 Things to keep in mind when exploring this implementation is:
  * platform specificity. Windows, Unix, and Linux filesystems are arranged differently.
  * the first relevance statement may depend on the machine to be Connected at the time of evaluation, so new components that are not connected at evaluation time will not be reported.


### New Plan:
Prompt user for:
 * site type
 * site name
 * Use this fixlet, 
	Relevance: Q: `if exist values of settings "ProvisioningTime" of client then value of setting "ProvisioningTime" of client else error "not set"`
	Actionscript: `setting "Test Setting"="Test Value 1" on "{parameter "action issue date" of action}" for client`

