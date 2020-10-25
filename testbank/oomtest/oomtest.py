#!/usr/bin/env python3
import subprocess, sys

def test_name():
    print("Out of Memory test")

def run_command(cmd):
    c = cmd.split()
    print("Command executed : " + cmd)
    process = subprocess.Popen(c, stdout=subprocess.PIPE, universal_newlines=True)

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
    cmd = ('grep -i kill /var/log/messages*')
    test_name()
    run_command(cmd)






