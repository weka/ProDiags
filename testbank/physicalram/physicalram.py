#!/bin/bash
#run_once
    
# Globals
res="0"

echo "Testing Weka nodes physical RAM that is equal between hosts"

diff=`weka cluster host info-hw | grep -i "total:" | awk {'print $2'} | uniq | wc -l`
if [ "$diff" != "1" ]; then 
	echo "At least one of the hosts has RAM incorrectly allocated, please check with free -hl"
	rm -rf /tmp/host_info-hw.txt
	weka cluster host info-hw | grep -i "total:\|resolvedIP" | awk {'print $2'} > /tmp/host_info-hw.txt
	echo "Hosts has inconsistent physical RAM sizes installed:"
	tac /tmp/host_info-hw.txt
	rm -rf /tmp/host_info-hw.txt
        res="1"
fi

if [ "$res" == "1" ]; then
	exit 1
fi
