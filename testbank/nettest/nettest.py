#!/bin/bash
# Test to check on errors on all backend NICs using ethtool -S <device_name> which are up
#
# Global settings
res=""

# Looking for ethtool to to scan for port errors
which ethtool 1> /dev/null 2> /dev/null 
if [ $? -eq 1 ]; then
	echo "Ethtool not found"
	exit 1
fi

for f in /sys/class/net/*; do
	dev=$(basename $f)
	driver=$(readlink $f/device/driver/module)
	if [ $driver ]; then
		driver=$(basename $driver)
	fi
	addr=$(cat $f/address)
	operstate=$(cat $f/operstate)
	if [ "$operstate" == "up" ]; then
		echo "Looking at device name: $dev for errors"
		ethtool -S $dev|grep -i "err" | grep ": [1-9]"
		if [ $? -ne 1 ]; then
			echo "Some errors found on $dev device below:"
			ethtool -S $dev | grep -i "err"
			res="1"
		else
			echo "No errors found for $dev device name"
		fi
	fi
	#printf "%10s [%s]: %10s (%s)\n" "$dev" "$addr" "$driver" "$operstate"
done

if [ "$res" == "1" ]; then
	exit 1
fi

