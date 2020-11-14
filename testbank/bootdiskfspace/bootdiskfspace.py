#!/bin/bash
#Script to find out if there is enough free space on OS which have Weka installed under /opt/weka
# TODO:

# Globals
res="0"
usage="95" # Above this value result test would fail

echo "Test name: Find out if / partition has enough free space"
which hostname 1> /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
        echo "Hostname command not found"
else
        echo "Hostname: `hostname`"
        echo "IP address: `hostname -I`"
fi

cur_usage=`df -h / | awk {'print $5'} | sed 's/%//g' | tail -1`
if [ "$cur_usage" -ge "$usage" ]; then
	echo "The boot drive is almost full.."
	res="1"
fi


if [ "$res" -ne "0" ]; then
	exit 1
fi
