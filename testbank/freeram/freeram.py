#!/usr/bin/env python3
import subprocess, sys, socket

def test_name():
    print("Test name: Free RAM test")

def test_host():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print("Hostname: " + hostname)
    print("IP address: " + IPAddr)

def run_command(cmd):
    print("Command executed : " + cmd,flush=True)
    # Had to parse this command explictly since, Python doesn't like to add quotes in list properly
    process = subprocess.Popen(['free','-lh'], stdout=subprocess.PIPE, universal_newlines=True)

    # Little ugly, make a man fly and bird walk method to bypass grep error return code properly
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

if __name__=="__main__":
    cmd = ('free -lh')
    test_name()
    test_host()
    run_command(cmd)
