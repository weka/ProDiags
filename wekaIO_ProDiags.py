#!/usr/bin/env python3
from threading import Thread
import pathlib
from time import sleep
from random import randint
import os
import sys
import argparse
from scp import SCPClient
from paramiko import SSHClient,AutoAddPolicy
import json
import config
import traceback

def threaded(fn):
    """
    Decorator that puts decorated function in separate thread.
    """
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

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

    def pp_tests(self):
        print ("Available tests")
        for i,t in enumerate(self.tests):
            print ("%s. %s"%(i+1,t))

# Getting list of servers output from weka cluster host command performed locally on backend system
    def get_servers(self):
        lst = os.popen("weka cluster host -b | grep HostId | awk {'print $3'} | uniq | sort").read().split()
        if not lst:
            print('Could not find "weka cluster host" command in that system')
            sys.exit(1)
        else:
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
        server.copy(str(self.path.joinpath("testbank")),'/tmp')       
        self.results[server.host] = {}
        for test in [self.tests[i-1] for i in test_indexes]:
            results = server.run('/tmp/testbank/%s/%s.py'%(test,test))
            self.results[server.host][test]=results
        server.run('rm -rf /tmp/testbank')
        server.close()


    def get_errors_only(self):

        def errors_on_server(server_results):
            return server_results if server_results.get('status',0) == -124 else \
                   dict([(k,v) for (k,v) in server_results.items() if v['status']!=0])

        return dict([(server,errors_on_server(results)) for server,results in self.results.items()])

    def split_tests(self,test_indexes):
        first_server,all_servers = [],[]
        for i in test_indexes:
            test = self.tests[i-1] 
            lines = open(self.path.joinpath('testbank/%s/%s.py'%(test,test))).readlines()
            if "#run_once" in [x.lower().strip() for x in lines]:
                first_server.append(i)
            else:
                all_servers.append(i)
        return first_server,all_servers
            
    def run_tests(self,test_indexes=[],run_all=False):
        if run_all:
            test_indexes = [i+1 for i in range(len(self.tests))]
        self.results = {}
        run_on_first_server,run_on_all_servers = self.split_tests(test_indexes)
        first_server_thread = self.run_tests_on_server(self.servers[0],test_indexes)
        other_servers_threads = [self.run_tests_on_server(server,run_on_all_servers) for \
                   server in self.servers[1:]]
        threads = [first_server_thread]+other_servers_threads                              
        for thread in threads:
            thread.join()

# MAIN and arguments parser
if __name__=="__main__":
    tester = Tester()
    parser = argparse.ArgumentParser()
    parser.add_argument("-l","--list",  action='store_true',help="Show all available tests")
    parser.add_argument("-r","--run", nargs='+',metavar='N',type=int,help="Run specified tests")
    parser.add_argument("-ra","--runall", action='store_true',help="Run all available tests")
    parser.add_argument("-e", "--errors_only", action='store_true',help="Show failed tests only") 
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        args=parser.parse_args()
    if args.list:
        tester.pp_tests()
    elif args.run:
        tester.run_tests(args.run)
    elif args.runall:
        tester.run_tests(run_all=True)
# Print test results
    res = tester.get_errors_only() if args.errors_only else tester.results
    print (json.dumps(res,sort_keys=True, indent=4))
