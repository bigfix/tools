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
