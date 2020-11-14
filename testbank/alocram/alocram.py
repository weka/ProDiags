#!/bin/bash
#run_once
    
# Globals
res="0"

echo "Test name: Testing Weka allocated RAM that is equal between hosts"
which hostname 1> /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
	echo "Hostname command not found"
else
	echo "Hostname: `hostname`"
	echo "IP address: `hostname -I`"
fi
diff=`weka cluster host -b -J | grep -i memory | sed 's/^ *//g' | awk {'print $2'} | sed 's/,//g' | uniq | wc -l`
if [ "$diff" != "1" ]; then 
	echo "At least one of the hosts has wrong RAM allocated, please check with weka cluster host -b -J command" 
        res="1"
fi

if [ "$res" == "1" ]; then
	exit 1
fi
