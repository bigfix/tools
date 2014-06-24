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

## Parameters
### Import
* `-s, --source-db-name` (*default: BFEnterprise*)
* `-b, --target-db-backup` .bak file location
* `-t, --target-db-name`

### SQL Server
#### Connection
* `-H, --sql-server-host` (*default: localhost*)
* `-p, --sql-server-port` (*default: 1433*)

#### Authentication
* `-w, --sql-server-windows-auth` for Windows authentication (*default: on*)
* `-u, --sql-server-user` for user password authentication
* `--sql-server-password` for user password authentication

### Site Private Key
* `-l, --site-pvk-location`
* `--site-pvk-password`

### Information
* `-h, --help`

## Example
Tested on `bran` a Windows Server 2012 environment:
- Microsoft SQL Server 2012
- IBM Endpoint Manager 9.1.1088.0 - Root Server
- python-3.3.5.amd64
- pyodbc-3.0.7.win-amd64-py3.3
- pywin32-218.win-amd64-py3.3
- psutil-2.1.1.win-amd64-py3.3

In this example, the following will allow `bran` to use another BFEnteprise database, `summer`.
 
    python warg.py --target-db-backup C:\winterfell\summer_BFEnterprise.bak
                   --sql-server-host localhost
                   --site-pvk-location C:\winterfell\license.pvk
                   --site-pvk-password bigfix

### How it works
The Root Server's credentials on source, `bran`, are moved to the target database, `summer`. Then, the IBM Endpoint Manager Admin tool is used to re-sign the data on `summer` with the migrated credentials. The IBM Endpoint Manager binaries on `bran` are untouched and the Root Server is functional with data from `summer`.
