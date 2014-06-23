#!/usr/bin/python

import subprocess, os, shutil, time, winreg, sys
import win32api, win32gui, win32con, win32process
import pyodbc
import psutil
import datetime, calendar

from queue import Queue
from threading import Thread
from argparse import ArgumentParser
from getpass import getpass

class BESAdmin:
  __run = {'resigninvalidsignatures':
            {'options': '/findInvalidSignatures /resignInvalidSignatures',
             'tasks':   [{'window': 'Admin Tool',
                          'button': ['OK']},
                         {'window': 'Resign Invalid Content?',
                          'button': ['&Yes', 'Yes']},
                         {'window': 'Admin Tool',
                          'button': ['OK']}]},

           'resignsecuritydata':
             {'options': '/resignSecurityData',
              'tasks':   [{'window': 'Admin Tool',
                           'button': ['OK']}]},

           0:
             {'options': '',
              'tasks':  [{'window': 'IBM Endpoint Manager Administration Tool',
                          'button': ['OK']}]}}

  def __init__(self, location, password):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                         r'SOFTWARE\BigFix\Enterprise Server',
                         access=winreg.KEY_WOW64_32KEY | winreg.KEY_QUERY_VALUE)
    server_location = winreg.QueryValueEx(key, 'EnterpriseServerFolder')[0]
    key.Close()
    besadmin_location = os.path.join(server_location, 'BESAdmin.exe')

    self._run_command = '"{0}" ' \
                        '/sitePvkLocation:"{1}" ' \
                        '/evalExpressPassword:{2}'.format(besadmin_location,
                                                          location, 
                                                          password)

  def __exists_window_from_pid(self, pid):
    exists = False
    def __enum_handler(hwnd, *args):
      nonlocal exists
      _, p = win32process.GetWindowThreadProcessId(hwnd)
      if p == pid and win32gui.IsWindowVisible(hwnd) \
         and win32gui.IsWindowEnabled(hwnd):
        exists = True
        return

    win32gui.EnumWindows(__enum_handler, None)
    return exists

  def __close_button(self, hwnd, buttons):
    for button in buttons:
      hbutton = win32gui.FindWindowEx(hwnd, 0, 'Button', button)
      if hbutton != 0:
        win32api.PostMessage(hbutton, win32con.WM_LBUTTONDOWN, 
                             win32con.MK_LBUTTON, 0)
        win32api.PostMessage(hbutton, win32con.WM_LBUTTONUP, 
                             win32con.MK_LBUTTON, 0)
        return
      # else: todo: raise

  def __close(self, task, pid):
    time.sleep(.42)    
    hwnd = win32gui.FindWindowEx(0, 0, '#32770', task['window'])
    wait = 1
    while hwnd == 0:
      if wait == 512:
        if psutil.Process(pid).cpu_percent() == 0 \
           and self.__exists_window_from_pid(pid):
          # sometimes a besadmin window crashes...
          return
      time.sleep(wait)
      wait *= 2

      hwnd = win32gui.FindWindowEx(0, 0, '#32770', task['window'])

    self.__close_button(hwnd, task['button'])

  def __worker(self, queue, pid):
    while True:
      task = queue.get()
      self.__close(task, pid)
      queue.task_done()

  def run(self,command=None):
    if command is None:
      command = 0

    if command not in self.__run:
      return # todo: raise

    config = self.__run[command]
    process = subprocess.Popen('{0} {1}'.format(self._run_command, 
                                                config['options']))

    queue = Queue()
    for task in config['tasks']:
      queue.put(task)

    thread = Thread(target=self.__worker, args=(queue, process.pid,))
    thread.daemon = True
    thread.start()

    queue.join()
    if self.__exists_window_from_pid(process.pid):
      return # todo: raise

class Authentication:
  def __init__(self, windows, user=None, password=None, prompt=False):
    if (windows and ((user is not None) or (password is not None))) \
     or ((not windows) and ((user is None) or (password is None))):
      raise Exception(
        'Must specify either Windows or SQL server authentication')

    self.windows = windows

    if prompt and not windows:
      if user is None:
        self.user = input('Enter user for SQL server: ')
      else:
        self.user = user

      if password is None:
        self.password = getpass(
          'Enter password for SQL server user "{0}": '.format(
            args.sql_server_user))
      else:
        self.password = password

class Database:
  def __init__(self, host, port, auth, name=None):
    self.host = None
    self.port = None
    self.auth = None
    self.name = None

    self._connection = None
    self.cursor = None

    self.connect(host, port, auth, name)

  def connect(self, host=None, port=None, auth=None, name=None):
    if self._connection is not None:
      self._connection.close()
      self.cursor = None

    if host is not None:
      self.host = host
    if port is not None:
      self.port = port
    if auth is not None:
      self.auth = auth
    if name is not None:
      self.name = name

    connect = 'DRIVER={{SQL Server}};' \
              'SERVER={0};'.format(self.host)
    if self.port is not None:
      connect += 'PORT={0};'.format(port)
    if not self.auth.windows:
      connect += 'UID={0};PWD={1};'.format(self.auth.user, self.auth.password)
    if self.name is not None:
      connect += 'DATABASE={0};'.format(self.name)

    self._connection = pyodbc.connect(connect,
                                      autocommit=True)
    self.cursor = self._connection.cursor()

  def execute(self, sql, *args):
    return self.cursor.execute(sql, *args)

  def exists_table(self, table):
    return self.execute("""\
select 1 from INFORMATION_SCHEMA.TABLES 
where TABLE_CATALOG = DB_NAME() 
and TABLE_NAME like ?""", table).fetchone() != None

class Services:
  def __run(self, x, name):
    try:
      subprocess.check_call('{0} {1} {2}'.format('net', x, name),
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    except:
      return -1
    return 0 

  def start(self, name, force=None):
    if force is None:
      force = False

    if self.is_stopped(name) or force:
      self.__run('start', name)
    return # todo: raise

  def stop(self, name, force=None):
    if force is None:
      force = False

    if self.is_running(name) or force:
      self.__run('stop', name)
    return # todo: raise

  def __check(self, name):
    try:
      out = subprocess.check_output('sc query {0}'.format(name),
                                    universal_newlines=True)
      if 'STOPPED' in out:
        return 1
      elif 'RUNNING' in out:
        return 0
      else:
        return -1
    except:
      return -1

  def is_stopped(self, name):
    return self.__check(name) == 1

  def is_running(self, name):
    return self.__check(name) == 0

class Warg:
  def __init__(self, besadmin, db, services):
    self.besadmin = besadmin
    self.db = db
    self.services = services

  def __stop_services(self):
    for service in ['BESClient' 'FillDB', 'BESGather', 'GatherDB', \
                    'BESRootServer', 'BESWebReportsServer']:
      self.services.stop(service)

  def __restore_db(self, source_db_name, target_db_backup):
    now = calendar.timegm(datetime.datetime.now().timetuple())
    
    target_db_name = source_db_name
    if source_db_name == 'BFEnterprise':
      source_db_name = 'source_BFEnterprise_{0}'.format(now)
      self.db.execute(""" \
alter database BFEnterprise
modify Name = {0}""".format(source_db_name))

    target_file_name = 'target_BFEnterprise_{0}'.format(now)

    mdf_location = self.db.execute(""" \
select physical_name from sys.master_files
where database_id = DB_ID(N'{0}')
and type_desc = 'ROWS'""".format(source_db_name)).fetchone()[0]
    mdf_location = os.path.abspath(os.path.join(mdf_location, os.pardir))

    ldf_location = self.db.execute(""" \
select physical_name from sys.master_files
where database_id = DB_ID(N'{0}')
and type_desc = 'LOG'""".format(source_db_name)).fetchone()[0]
    ldf_location = os.path.abspath(os.path.join(ldf_location, os.pardir))

    self.db.execute(""" \
create table #filelistonly_result
(
  LogicalName nvarchar(128),
  PhysicalName nvarchar(260),
  Type char(1),
  FileGroupName nvarchar(128),
  Size numeric(20,0),
  MaxSize numeric(20,0),
  FileId bigint,
  CreateLSN numeric(25,0),
  DropLSN numeric(25,0),
  UniqueId uniqueidentifier,
  ReadOnlyLSN numeric(25,0),
  ReadWriteLSN numeric(25,0),
  BackupSizeInBytes bigint,
  SourceBlockSize int,
  FileGroupId int,
  LogGroupGUID uniqueidentifier,
  DifferentialBaseLSN numeric(25,0),
  DifferentialBaseGUID uniqueidentifier,
  IsReadOnly bit, 
  IsPresent bit, 
  TDEThumbprint varbinary(32)
)""")

    self.db.execute(""" \
insert into #filelistonly_result
exec('restore filelistonly from disk = ''{0}''')""".format(target_db_backup))

    bak_db_name = self.db.execute(""" \
select LogicalName from #filelistonly_result
where Type = 'D'""").fetchone()[0]

    bak_log_name = self.db.execute(""" \
select LogicalName from #filelistonly_result
where Type = 'L'""").fetchone()[0]

    self.db.execute(""" \
drop table #filelistonly_result""")

    self.db.execute(""" \
restore database {0}
from disk='{1}'
with move '{2}' to '{3}',
move '{4}' to '{5}'""".format(
                         target_db_name,
                         target_db_backup, 
                         bak_db_name, os.path.join(mdf_location, 
                                        '{0}.mdf'.format(target_file_name)),
                         bak_log_name, os.path.join(ldf_location, 
                                         '{0}.ldf'.format(target_file_name))))

    while self.db.cursor.nextset():
      pass

    return (source_db_name, target_db_name)

  def __change_db(self, source_db_name, target_db_name):
    self.__delete_source_data(source_db_name, target_db_name)
    self.__migrate_actionsite(target_db_name)

  def __delete_source_data(self, source_db_name, target_db_name):
    self.db.connect(name=target_db_name)
    self.db.execute(""" \
delete from ADMINFIELDS where FieldName = 'PendingSiteCertificates'""")

    self.db.execute(""" \
update A
  set FieldContents = HA.FieldContents
from ADMINFIELDS A
inner join {0}.dbo.ADMINFIELDS HA
on HA.FieldName = A.FieldName \
and A.FieldName in ('ClientCACertificate_0', 'Masthead', \
                    'ServerSigningCertificate_0', 'SiteCertificate')
""".format(source_db_name))

    self.db.execute(""" \
update ADMINFIELDS
  set IsDeleted = 1
where FieldName like '%Certificate_[1-9]'""")

    self.db.execute(""" \
insert into CERTIFICATES \
(SHA1Hash, Subject, Issuer, SerialNumber, Certificate, Revocations, \
  ManyVersion, OriginServerID, OriginSequence) \
select SHA1Hash, Subject, Issuer, SerialNumber, Certificate, Revocations, \
  ManyVersion, OriginServerID, OriginSequence \
from {0}.dbo.CERTIFICATES""".format(source_db_name))

    self.db.execute(""" \
update CUSTOM_SITES
  set SubscribeSMIME = NULL,
      UnsubscribeSMIME = NULL""")

    self.db.execute(""" \
update REPLICATION_SERVERS
  set IsDeleted = 1
where ServerID != 0""")

    self.db.execute(""" \
update REPLICATION_SERVERS
  set DNS = '240.0.0.0',
      URL = 'http://240.0.0.0'""")

    self.db.execute(""" \
update COMPUTER_REGISTRATIONS
  set IPAddress = '240.0.0.0',
      Subnet = '240.0.0.0/4'""")

    self.besadmin.run('resignsecuritydata')

  def __migrate_actionsite(self, target_db_name):
    self.db.connect(name=target_db_name)
    old_site_id = self.db.execute(""" \
select SiteID from SITENAMEMAP where Sitename = 'ActionSite'""").fetchone()[0]
    self.db.execute(""" \
delete from SITENAMEMAP where Sitename = 'ActionSite'""")

    self.besadmin.run()

    new_site_id = self.db.execute(""" \
select SiteID from SITENAMEMAP where Sitename = 'ActionSite'""").fetchone()[0]
    self.db.execute("""
update QUESTIONRESULTS 
  set SiteID = ?
where SiteID = ?""", new_site_id, old_site_id)
    self.db.execute("""
update LONGQUESTIONRESULTS 
  set SiteID = ?
where SiteID = ?""", new_site_id, old_site_id)

    self.besadmin.run('resigninvalidsignatures')

    self.db.execute(""" \
delete O from LOCAL_OBJECT_DEFS O
inner join Versions V
on O.Sitename = 'ActionSite' 
and V.Sitename = O.Sitename 
and O.ID = V.ID 
and O.Version != V.LatestVersion""")    

  def __start_server_services(self):
    for service in ['FillDB', 'BESGather', 'GatherDB', 'BESRootServer']:
      self.services.start(service, force=True)

  def __start_client_service(self):
    folders = []

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                         r'SOFTWARE\BigFix\EnterpriseClient',
                         access=winreg.KEY_WOW64_32KEY | winreg.KEY_QUERY_VALUE)
    client_location = winreg.QueryValueEx(key, 'EnterpriseClientFolder')[0]
    key.Close()

    folders.append(os.path.join(client_location, 'KeyStorage'))
    folders.append(os.path.join(client_location, '__BESData', 'BES Support'))
    folders.append(os.path.join(client_location, '__BESData', 'actionsite'))
    folders.append(os.path.join(client_location, '__BESData', 'mailboxsite'))

    for folder in folders:
      if os.path.isdir(folder):
        shutil.rmtree(folder)

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                         r'SOFTWARE\BigFix\EnterpriseClient\GlobalOptions',
                         access=winreg.KEY_WOW64_32KEY | winreg.KEY_ALL_ACCESS)
    winreg.DeleteValue(key, 'ComputerID')
    key.Close()

    self.services.start('BESClient', force=True)

  def __start_services(self):
    self.__start_server_services()
    self.__start_client_service()

  def change_credentials(self, source_db_name, target_db_backup, 
                         target_db_name=None):
    self.__stop_services()
    if target_db_backup is not None:
      (source_db_name, target_db_name) = self.__restore_db(source_db_name, 
                                                           target_db_backup)
    self.__change_db(source_db_name, target_db_name)
    self.__start_services()

def parse_args():
  description = """\
Change the credentials of a target IBM Endpoint Manager database
 (BFEnterprise) with a source environment"""

  usage = """Usage: python warg.py [options]

{0}

Options:
  -s, --source-db-name DBNAME       source database name 
                                    (default: BFEnterprise)

  -t, --target-db-name DBNAME       target database name
  -b, --target-db-backup LOCATION   target database backup location

  -H, --sql-server-host HOST        SQL server host 
                                    (default: localhost)
  -p, --sql-server-port PORT        SQL server port 
                                    (default: 1433)
  -w, --sql-server-windows-auth     SQL server Windows authentication 
                                    (default: on)
  -u, --sql-server-user USER        SQL server username (for user password 
                                    authentication)
  --sql-server-password PASSWORD    SQL server password (for user password 
                                    authentication)

  -l, --site-pvk-location LOCATION  site private key location
  --site-pvk-password PASSWORD      site private key password

  -h, --help                        print this help text and exit
  """.format(description)

  argparser = ArgumentParser(description=description,
                             usage=usage,
                             add_help=False)

  argparser.add_argument('-s', '--source-db-name', default='BFEnterprise')

  argparser.add_argument('-t', '--target-db-name')
  argparser.add_argument('-b', '--target-db-backup')

  argparser.add_argument('-H', '--sql-server-host', default='localhost')
  argparser.add_argument('-p', '--sql-server-port', default=1433)
  argparser.add_argument('-w', '--sql-server-windows-auth', default=True,
                         action='store_true')
  argparser.add_argument('-u', '--sql-server-user')
  argparser.add_argument('--sql-server-password')

  argparser.add_argument('-l', '--site-pvk-location')
  argparser.add_argument('--site-pvk-password')

  argparser.add_argument('-h', '--help')

  if '-h' in sys.argv or '--help' in sys.argv:
    print(usage)
    sys.exit()

  args = argparser.parse_args()

  if (args.target_db_backup is None) and (args.target_db_name is None):
    args.target_db_backup = input('Enter location for target database backup: ')

  args.sql_server_auth = Authentication(windows=args.sql_server_windows_auth,
                                        user=args.sql_server_user,
                                        password=args.sql_server_password,
                                        prompt=True)

  if args.site_pvk_location is None:
    args.site_pvk_location = input('Enter location for site private key: ')

  if args.site_pvk_password is None:
    args.site_pvk_password = getpass('Enter password for site private key: ')    

  return args

def main():
  args = parse_args()

  warg = Warg(BESAdmin(args.site_pvk_location, 
                       args.site_pvk_password),
              Database(args.sql_server_host, 
                       args.sql_server_port, 
                       args.sql_server_auth),
              Services())
  warg.change_credentials(args.source_db_name,
                          args.target_db_backup,
                          args.target_db_name)

if __name__ == '__main__':
  main()
