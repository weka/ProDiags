#!/bin/bash

# Setting return value
ret=""

function scriptname () {
# Script descriptive name
if [ "$name_enabled" == "true" ]; then
	echo "Checking RAM state for errors"
fi
}


function startscript () {
# Put your stuff here
find /sys -name ce\*  | while read f; do echo "$f $(cat $f)"; done
if [ $? -ne 0 ]; then
	echo "Errors found in currently installed RAM"
	rm -rf /tmp/dmesg_output.txt /tmp/ram_error.txt 1> /dev/null 2> /dev/null
	dmesg > /tmp/dmesg_output.txt
	cat /tmp/dmesg_output.txt | grep -i -A7 "HANDLING MCE MEMORY ERROR" > /tmp/ram_error.txt
	cat /tmp/ram_error.txt
	ret="1"	
else
	ret="0"
fi

}

function checkstatus () {
if [ $ret -ne 0 ]; then
	exit 1
else
	exit 0
fi

}

### MAIN ###
scriptname
startscript
checkstatus
