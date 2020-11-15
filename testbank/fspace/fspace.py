#!/usr/bin/env python3
import subprocess, sys, os, socket, shutil

def test_name():
    print("Test name: Basic disk usage test")

def test_host():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print("Hostname: " + hostname)
    print("IP address: " + IPAddr)


def get_usage(path):
   BytesPerGB = 1024 * 1024 * 1024
   minimum_space = 1053573120 # 1GiB of free space is minimum
   (total, used, free) = shutil.disk_usage(path)
   print ("Path tested: " + path)
   print ("Total: %.2fGiB" % (float(total)/BytesPerGB))
   print ("Used:  %.2fGiB" % (float(used)/BytesPerGB))
   print ("Free:  %.2fGiB" % (float(free)/BytesPerGB))
   if free < minimum_space:
      print ("The free space on: " + path," is too low")
      set_err('1')

def set_err(ret_code):
   if ret_code == '1':
       sys.exit(1)

if __name__=="__main__":
   ret_code = ''
   test_name()
   test_host()
   get_usage('/')
   get_usage('/opt/weka')
