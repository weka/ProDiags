
n.n.n / 2021-08-16
==================

  * Fixed ssdtest to allow proper NVMe spare defaults handling. Fixed support for both IPMItool and IPMIutil packages specifically for Hitachi case. Changed default logs upload behaviour to NO
  * Fixed minior bug in physical RAM comparison test
  * Minor fix in version update
  * Added an option for user to agree to upload the logs for analysis. Added a standalone version without the .py extension, avoid extra python libraries installation. For ipmi tests, added localalized ipmiutil package for RH / Centos Linux distros. MC (minio client is not added as we assume there is no internet available)
  * Minor bug fix in update
  * Fixed log collection on list of tests command
  * Fixed log file closing if running with full file verbosity
  * Minor cosmetic fixes and fixed SSD test for mismatching ACTIVE vs INACTIVE SSD drives
  * Removed comma
  * Updaed version file to be 1.0
  * Added support for versions 3.9.3, 3.9.2, 3.9.1. Cosmetics on output, internet connection verification, root user verification. Version output. Support for output of tests to look cleaner. If no -e specified everything is spit on the screen.
  * Added internet check before update, added root user check
  * Added support for version 3.9.3, fixed tailing outputs for IPMI tests
  * Minor fix in collect_diags.sh
  * Fixed logs collection to verify internet connection If internet connection not found, won't collect logs
  * Fixes in IPMI scripts to support ipmiutil download from 3rd party location for CentOS 8 Fixed memtest, added support for weka 3.10.x-beta. Small bug fixes
  * Added ECC CPU, and general critical BMC errors test, minor bugs and fixes Beatified test outputs according to David H. request
  * Fixed some minior issues and cosmetics output
  * Minor fix for running minio client in special SHELL environments
  * Updated README file with latest version number
  * Version 0.7 11/19/2020 Added ECC RAM test, added logs collection automatically to compatible S3 bucket. Small fixes and addons
  * Added fspace test to calculate free space on boot partition and weka partition. If space below 1GiB - test would fail
  * Fixed output and errors in some tests with Jacky feedback Added hostname and IP addresses return in tests Minor typos and fixes
  * Added Free boot device test, Physical installed RAM allocation test Added setup.sh to install python packages as needed
  * Updated Readme file
  * Added beautifier for output to text and file of reported logs Added freespace test for Weka mounted partition to calculated required space for Weka installation
  * Updated version to 0.3
  * Added support for version 3.9.0 for performing SSD test as weka output is changed for weka cluster drive and weka cluster host commands
  * Updated Readme file some more
  * Removed some bogus directories and updated version & readme files
  * Added -u option to perform udpate if VERSION file is updated
  * Added an RAM allocation test for weka, if more than one hosts reports different Memory size, the test would fail
  * Added nettest for scanning each backend UP port for RX/ TX or any other physucal error
  * Added ssdtest to look up for issues with SSD
  * Added an option within test to run only once if configured
  * Fixed the tests to return the correct return code - handled interesting bash conditions
  * Added basic tests to test RAM, Out of Memory and RAM test in proc for errors Updated CHANGELOG
  * Modified tests to support .py Added error filter as command line parameter -e
  * Minor cosmetic changes
  * Modified tool to support .py tests (tests not modifed yet) Added support for external SSH configuration Added some basic timeout functionality
  * Initial upload to github code from BitBucket
#!/usr/bin/env python3
import pathlib,os,sys,argparse,json,config,traceback,requests,io,tarfile,socket
from threading import Thread
from time import sleep
from random import randint
from scp import SCPClient
from paramiko import SSHClient,AutoAddPolicy
import os

def threaded(fn):
    """
    Decorator that puts decorated function in separate thread.
    """
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def remove_blank_lines(text):
    return os.linesep.join([s for s in text.splitlines() if s.strip()])


class Generic:
    
    def __init__(self):
        self.path = pathlib.Path(__file__).parent.absolute()
  
    def update(self):
        resp = requests.get(config.TAR_URL)
        fo = io.BytesIO(resp.content)
        tar = tarfile.open(fileobj = fo)
        cur_version = float(tar.extractfile("./VERSION").read().decode("utf-8").strip())
        my_version = float(open(self.path.joinpath("VERSION")).read().strip())                           
        if cur_version>my_version:
            answer = input("There is a new version, do you want to update? ((Y)es/(N)o)")
            if answer.lower() in ["y","yes"]:
                tar.extractall()
        else:
            print ("No new updates found")
    
    def version(self):
        lines = os.popen("cat VERSION").read().strip()
        tools_version = str(lines)
        print ('WekaIO_ProDiags version: ' +tools_version)

    def test_internet(self):
        website = ("lib.ru")
        if socket.gethostbyname(website) != "81.176.66.163":
            print("The host is not connected to the internet, unable to check for updates")
            sys.exit(1)
        else:
            return 0

    def testuser(self):
        user = os.getuid()
        if user != 0:
            print("This program requires root privileges. Run as root or using 'sudo'.")
            sys.exit()
        else:
            return 0

# Connection class to perform SSH commands on remote server
class Connection:
    def __init__(self,server):
        self.host = server['host']
        self.username = server['username']
        self.password = server['password']
        self.ssh = None
        self.scp = None

    def open(self):
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(self.host, username=self.username, password=self.password,
                         timeout = config.SSH_CONNECT_TIMEOUT,auth_timeout = config.SSH_AUTH_TIMEOUT)
        self.scp = SCPClient(self.ssh.get_transport())

    def close(self):
        if self.ssh:
            self.ssh.close()
        if self.scp:
            self.scp.close()

    def copy(self,source,dest):
        self.scp.put(source,recursive=True,remote_path = dest)

    def run(self,cmd):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd,timeout = config.SSH_EXEC_TIMEOUT)
            status = stdout.channel.recv_exit_status()
            response = stdout.read()
            error = stderr.read()
            return {'status':status,'response':response.decode("utf-8") ,'error':error.decode("utf-8")}
        except:
            return {'status': -123,
                    'description':'Failed to run command',
                    'traceback':traceback.format_exc()}

# Tester class
class Tester:

    def __init__(self):
        self.path = pathlib.Path(__file__).parent.absolute()
        self.servers = self.get_servers()
        self.tests = self.get_tests()
        self.results = {}
        self.json = True
        self.out = True
        self.errors_only = False
        self.file = sys.stdout
        self.log_file = open('/var/log/WekaIO_ProDiags.log','w')

    def print(self,*args):
        print(*args,file = self.file)
        print(*args,file = self.log_file)
        

    def pp_tests(self):
        print ("Available tests:")
        for i,t in enumerate(self.tests):
            print ("%s. %s"%(i+1,t))

    def get_weka_version(self):
        lines = os.popen("/usr/bin/weka version | awk -F. {'print $1\".\"$2'}").readlines()
        for l in lines:
            l=l.strip()
            if l.startswith("*"):
                return l[1:].strip()
        return 0 #just in case


    # Getting list of servers output from weka cluster host command performed locally on backend system
    def get_servers(self):
        ver = self.get_weka_version()
        if ver in ("3.9","3.10","3.12"):
            lst = os.popen("/usr/bin/weka cluster host -b | grep UP | awk {'print $3'} | sed 's/,//g' | uniq | sort").read().split()
        elif ver=="3.8":
            lst = os.popen("/usr/bin/weka cluster host -b | grep HostId | awk {'print $3'} | uniq | sort").read().split()
        else:
            print('Weka version '+ver+' is not supported by WekaIO_ProDiags tool')
            sys.exit(1)
        return [Connection({'host':ip,'username':config.USERNAME,'password':config.PASSWORD}) for ip in lst]

    # Testbank directory within the tool directory includes the tests fo runtime
    def get_tests(self):
        return [f.name for f in os.scandir(self.path.joinpath("testbank")) if f.is_dir()]     

    # Multithreaded connection to N servers and execute specified tests according to process:
    # 1. Open connection
    # 2. Clean remote server for exsting tests / outputs logs
    # 3. Copy updated testbank to remote server
    # 4. Execute the required tests on server
    @threaded
    def run_tests_on_server(self,server,test_indexes):
        try:
            server.open()
        except:
            self.results[server.host] = {'status': -124,
                                         'description':'Failed to open SSH connection',
                                         'traceback':traceback.format_exc()}
            return            
        server.run('rm -rf /tmp/testbank')
        server.run('rm -rf /tmp/lib')
        server.copy(str(self.path.joinpath("testbank")),'/tmp')       
        server.copy(str(self.path.joinpath("lib")),'/tmp')       
        self.results[server.host] = {}
        for test in [self.tests[i-1] for i in test_indexes]:
            parameter = ' a' if not self.errors_only else ''
            results = server.run('/tmp/testbank/%s/%s.py%s'%(test,test,parameter))
            if self.out:
                if 'response' in results:
                    resp = remove_blank_lines(results['response'])
                    errs = remove_blank_lines(results['error'])
                    if resp:
                        self.print(resp)
                    if errs:
                        self.print(errs)
            self.results[server.host][test]=results
        server.run('rm -rf /tmp/testbank')
        server.run('rm -rf /tmp/lib')
        server.close()


    def get_errors_only(self):

        def errors_on_server(server_results):
            return server_results if server_results.get('status',0) == -124 else \
                   dict([(k,v) for (k,v) in server_results.items() if v['status']!=0])

        return dict([(server,errors_on_server(results)) for server,results in self.results.items()])

    # If #run_once string found in specific test, test would be executed on one of the servers once
    def split_tests(self,test_indexes):
        first_server,all_servers = [],[]
        for i in test_indexes:
            test = self.tests[i-1] 
            lines = open(self.path.joinpath('testbank/%s/%s.py'%(test,test))).readlines()
            lines = [x.lower().strip() for x in lines]
            if "#dont_run" not in lines:
                if "#run_once" in lines:
                    first_server.append(i)
                else:
                    all_servers.append(i)
        return first_server,all_servers
            
    def run_tests(self,test_indexes=[],run_all=False):
        if run_all:
            test_indexes = [i+1 for i in range(len(self.tests))]
        self.results = {}
        run_on_first_server,run_on_all_servers = self.split_tests(test_indexes)
        first_server_thread = self.run_tests_on_server(self.servers[0],run_on_first_server+run_on_all_servers)
        other_servers_threads = [self.run_tests_on_server(server,run_on_all_servers) for \
                   server in self.servers[1:]]
        threads = [first_server_thread]+other_servers_threads                              
        for thread in threads:
            thread.join()

    def print_report(self):
        res = self.get_errors_only() if self.errors_only else self.results
        if res:
            if self.json:
                self.print (json.dumps(res,sort_keys=True, indent=4))
            self.log_file.close()
            os.system('./collect_diags.sh')
        
# MAIN and arguments parser
if __name__=="__main__":
    tester = Tester()
    generic = Generic()
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--version",  action='store_true',help="WekaIO_ProDiags version")
    parser.add_argument("-u","--update",  action='store_true',help="Software update")
    parser.add_argument("-l","--list",  action='store_true',help="Show all available tests")
    parser.add_argument("-r","--run", nargs='+',metavar='N',type=int,help="Run specified tests")
    parser.add_argument("-ra","--runall", action='store_true',help="Run all available tests")
    parser.add_argument("-e", "--errors_only", action='store_true',help="Show failed tests only")
    parser.add_argument("-nj", "--nojson", action='store_true', help = "no JSON report")
    parser.add_argument("-no", "--nooutput", action='store_true', help = "no scripts output")
    parser.add_argument('-f','--file', type=argparse.FileType('w'), default=sys.stdout,
                         metavar='PATH',
                        help="Output file (default: standard output)")
    
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        args=parser.parse_args()
    if args.nojson:
        tester.json = False
    if args.nooutput:
        tester.out = False
    if args.errors_only:
        tester.errors_only = True
    tester.file = args.file
    if args.update:
        generic.test_internet()
        generic.update()
        sys.exit(0)
    elif args.version:
        generic.version()
        sys.exit(0)
    elif args.list:
        generic.testuser()
        tester.pp_tests()
        sys.exit(0)
    elif args.run:
        generic.testuser()
        tester.run_tests(args.run)
    elif args.runall:
        generic.testuser()
        tester.run_tests(run_all=True)
    tester.print_report()
# Print test results
 
