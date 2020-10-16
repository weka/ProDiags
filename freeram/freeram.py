#!/bin/bash

# Setting return value
ret=""

function scriptname () {
# Script descriptive name
if [ "$name_enabled" == "true" ]; then
	echo "Checking if OS has enough RAM"
fi
}

function startscript () {

# Checking if OS has enough RAM for proper Weka.IO runtime - general requirement is 6.33G for each CPU core host if there is a cluster of 12 nodes
current_free_ram=`free -g | grep -i "mem" | awk {'print $3'}`
echo "Current amount of RAM that is free for Weka.IO on this node is: $current_free_ram"G""
ret="0"

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
