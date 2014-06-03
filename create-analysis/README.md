Command-line tool to create an analysis based on given relevance, then output the results as they come in.
This tools reads analysis queries from stdin and takes argument from command line. It would output the analysis
evaluation result as they come in.

Example:
	echo operating system | python create_analysis.py -a OS -d Test -s 127.0.0.1:52311 -u bigfix -p bigfix -t operator -n bigfix --insecure 
