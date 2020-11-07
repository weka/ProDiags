#!/bin/bash
#Script to find out if there is enough free space on OS which have Weka installed under /opt/weka
# TODO:

# Globals
res=""

echo "Find out if partition mounted with Weka has enough free space"

rm -rf /tmp/weka_exists* 1> /dev/null 2> /dev/null
find / -name 'data'|grep weka > /tmp/weka_exists.txt
cat /tmp/weka_exists.txt|grep -v wekatester > /tmp/weka_exists2.txt

cat /tmp/weka_exists2.txt | grep -i data |grep -i weka | head -1
if [ $? -eq 0 ]; then
	loc=`cat /tmp/weka_exists2.txt | grep -i data |grep -i weka | head -1`
	inst_loc=`dirname $loc`
	echo "Location of Weka installation is: $inst_loc"
else
	echo "Could not find Weka installation"
	res="1"
fi

num_of_cores=`grep -m 1 'cpu cores' /proc/cpuinfo | awk -F: {'print $2'}`
a="GiB"
required_free_space=`echo $((($num_of_cores*10)+26))`
actual_space=`df -h | grep -i "\$inst_loc" | head -1 | awk {'print $2'}|sed 's/[a-zA-Z]//g'`
space_missing=`echo $(($actual_space-required_free_space))`
echo "Actual space found on $inst_loc is: $actual_space$a"
echo "Number of CPU cores: $num_of_cores, require: $required_free_space$a"
if [ "$space_missing" -le 1 ]; then
	echo "Unfortunately, this partition $inst_loc is less than minimum required size of $required_free_space$a by missing $space_missing$a of free space"
	res="1"
fi

if [ "$res" -ne "0" ]; then
	exit 1
fi
