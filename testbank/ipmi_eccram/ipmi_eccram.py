#!/bin/bash
#
 
#Globals
res="0"
get_deps="true"

echo "Test name: Testing Weka backend server for ECC errors in RAM"
which hostname 1> /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
        echo "Hostname command not found"
else
        echo "Hostname: `hostname`"
        echo "IP address: `hostname -I`"
fi

function check_ipmitool()
{
# Looking for ipmitool availability
which ipmitool 1> /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
	echo "ipmitool not found"
	if [ "$get_deps" == "true" ]; then
		yum install ipmitool -y 1> /dev/null 2> /dev/null
		if [ $? -eq 1 ]; then
			echo "Could not install ipmitool properly"
			res="1"
		fi
	else
		res="1"
	fi
fi
}

function check_ipmiutil()
{
# Looking for ipmitool availability
which ipmiutil 1> /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
	echo "ipmiutil not found"
	if [ "$get_deps" == "true" ]; then
		yum install ipmiutil -y 1> /dev/null 2> /dev/null
		if [ $? -eq 1 ]; then
			echo "Could not install ipmiutil properly"
			res="1"
		fi
	else
		res="1"
	fi
fi
}

function check_dmidecode()
{
# Looking for IPMItool availabilit in BIOS
which dmidecode 1> /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
	echo "dmidecode tool not found"
	if [ "$get_deps" == "true" ]; then
		yum install dmidecode -y 1> /dev/null 2> /dev/null
		if [ $? -eq 1 ]; then
			echo "Could not install dmidecode properly"
			res="1"
		fi
	else
		res="1"
	fi
else
	dmidecode --type 38 | grep -i ipmi 1> /dev/null 2> /dev/null
	if [ $? -eq 1 ]; then
		echo "IPMI is not available on this system"
		res="1"
	fi
fi
}

function check_err()
{
# Function to set final exit status if something is failed beforehand
if [ "$res" == "1" ]; then
	exit 1
else
	return
fi
}

function start_test()
{
# Starting ECC DIMM test
rm -rf /tmp/ipmiutil_output.txt
ipmiutil sel -e > /tmp/ipmiutil_output.txt
cat /tmp/ipmiutil_output.txt |grep -i "bmc" |grep -i "asserted\|ecc" 1> /dev/null 2> /dev/null
if [ $? -eq 0 ]; then
	cat /tmp/ipmiutil_output.txt |grep -i "bmc" |grep -i "asserted\|ecc"
	res="1"
fi

}
# MAIN
check_ipmitool
check_ipmiutil
check_dmidecode
check_err
start_test

if [ "$res" == "1" ]; then
	exit 1
fi
