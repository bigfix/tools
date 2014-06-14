Change the credentials of a target IBM Endpoint Manager database (BFEnterprise) with a source environment

# Usage

## Prerequisites
- [python-3.3](https://www.python.org/downloads/)
- [pyodbc](https://code.google.com/p/pyodbc/)
- [pywin32](http://sourceforge.net/projects/pywin32/)
- [psutil](https://github.com/giampaolo/psutil)
- Microsoft SQL Server

## Environment
- Windows Server

## Example
Tested on `bran` a Windows Server 2012 environment:
- Microsoft SQL Server 2012
- IBM Endpoint Manager 9.1.1088.0 - Root Server
- python-3.3.5.amd64
- pyodbc-3.0.7.win-amd64-py3.3
- pywin32-218.win-amd64-py3.3
- psutil-2.1.1.win-amd64-py3.3

In this example, the following will allow `bran` to use another BFEnteprise database, `summer`.
 
    python warg.py --source-db-name bran_BFEnterprise
                   --target-db-name summer_BFEnterprise
                   --sql-server-host localhost
                   --sql-server-user sa
                   --sql-server-password bigfix
                   --site-pvk-location C:\winterfell\license.pvk
                   --site-pvk-password bigfix
