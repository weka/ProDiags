#!/usr/bin/env python3
import subprocess, sys

def test_name():
    print("Free RAM test")

def run_command(cmd):
    print("Command executed : " + cmd)
    # Had to parse this command explictly since, Pythong doesn't like to add quotes in list properly
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
    run_command(cmd)





