Create analysis
===

create_analysis is a Command-line tool to create an analysis based on given relevance, then output the results as they come in.
This tools reads analysis queries from stdin and takes argument from command line. It would output the analysis
evaluation result as they come in (the script will check every 10 second if the analysis is evaluated)

Parameters
---
  * `-a, --analysis_name`         Analysis name
  * `-d, --description`           Analysis description
  * `-h, --help`                  Print this help message and exit
  * `-s, --server SERVER[:PORT]`  REST API server and port
  * `-u, --user`                  REST API user
  * `-p, --password`              REST API password
  * `-t, --site_type`             Site type: master/custom/operator/external
  * `-n, --site_name`             Site-name

Example
---
	echo operating system | python create_analysis.py -a OS -d Test -s 127.0.0.1:52311 -u bigfix -p bigfix -t operator -n bigfix --insecure
