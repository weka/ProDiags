#!/usr/bin/env python3
import subprocess, sys, os, socket

def test_name():
    print("Test name: Basic memory test")

def test_host():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print("Hostname: " + hostname)
    print("IP address: " + IPAddr)

def create_file(filename,cmd):
    f = open(filename, "w")
    f.write(cmd)
    f.close()

def run_command(cmd):
    c = cmd.split()
    print("Command executed : " + cmd)
    process = subprocess.Popen(['sh',filename], stdout=subprocess.PIPE, universal_newlines=True)
    while True:
        output = process.stdout.readline()
        print(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            print('Return code : ', return_code)
            sys.exit(return_code)
            # Process has finished, read rest of the output 
            for output in process.stdout.readlines():
                print(output.strip())
            break

if __name__=="__main__":
    cmd = ('/usr/bin/find /sys -name ce\* | while read f; do echo "$f $(cat $f)"; done 2> /dev/null')
    filename = ('exec.sh')
    test_name()
    test_host()
    create_file(filename,cmd)
    run_command(cmd)
