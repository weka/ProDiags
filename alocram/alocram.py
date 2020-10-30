#!/bin/bash
#run_once
    
# Globals
res=""

echo "Testing Weka allocated RAM that is equal between hosts"

diff=`weka cluster host -b -J | grep -i memory | sed 's/^ *//g' | awk {'print $2'} | sed 's/,//g' | uniq | wc -l`
if [ "$diff" != "1" ]; then 
	echo "At least one of the hosts has wrong RAM allocated, please check with weka cluster host -b -J command" 
        res="1"
fi

if [ "$res" == "1" ]; then
	exit 1
fi
