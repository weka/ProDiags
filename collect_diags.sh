#!/bin/bash
# Tool to collect diagnostics and upload them to dedicated S3 compatible cloud bucket

# Default settings
url="http://ssh.i-clef.com:9000"
name="myminio"
bucketname="wekaioprodiags"
akey="YODAINSPACE"
skey="SPACEISINYODA"

now=$(date +"%m-%d-%Y_%H-%M-%S")
cluster_name=""
log_fname="/var/log/WekaIO_ProDiags.log"

#internet_host="lib.ru"
internet_host="adsba.com"

function check_outer_space()
{
# Function to check internet connection
ping -c 1 -i 1 -t 1 $internet_host 1> /dev/null 2> /dev/null
if [ $? -ne 0 ]; then
	echo "Internet connection is unavailable, not collecting logs"
	exit 1
fi


}

function get_minio()
{
#Getting Minio client
rm -rf mc 
rm -rf ~/root/.mc*
which curl 1> /dev/null 2> /dev/null
if [ $? -eq 1 ]; then
	exit 1
fi
curl -s http://ssh.i-clef.com/WekaIO_ProDiags/lib/mc -o mc
if [ -r mc ] ; then
	chmod +x mc
else
	exit 1
fi
}

function set_alias()
{
./mc alias set $name $url $akey $skey 1> /dev/null 2> /dev/null
}

function get_weka_cluster_info()
{
if [ -r /usr/bin/weka ]; then
	weka status > /tmp/weka_status_"$now".txt
	cluster_name=`cat /tmp/weka_status_"$now".txt | grep "cluster:" | awk {'print $2'}`
else
	return
fi
}

function get_tools_version()
{
cat VERSION > /tmp/VERSION_"$now".txt

}

function get_logs()
{
# Getting local logs
# Would exit if logs not found here..
if [ ! -r $log_fname ]; then
	clean
	exit 1
fi

cp $log_fname /tmp
mv /tmp/WekaIO_ProDiags.log /tmp/WekaIO_ProDiags_"$cluster_name"_"$now".log
tar cfz /tmp/WekaIO_ProDiags_"$cluster_name"_"$now".tgz /tmp/WekaIO_ProDiags_"$cluster_name"_"$now".log /tmp/VERSION_"$now".txt /tmp/weka_status_"$now".txt 2> /dev/null

}

function upload_logs()
{
# Function to upload local runtime logs to remote S3 bucket
./mc mb $name/$bucketname 1> /dev/null 2> /dev/null
./mc cp /tmp/WekaIO_ProDiags_"$cluster_name"_"$now".tgz $name/$bucketname 1> /dev/null
}

function clean()
{
# Clean up the mess
rm -rf /tmp/weka_status_"$now".txt
rm -rf /tmp/VERSION_"$now".txt
rm -rf /tmp/WekaIO_ProDiags_"$now".txt
rm -rf mc
rm -rf ~/root/.mc*
}

# MAIN
check_outer_space
get_minio
set_alias
get_weka_cluster_info
get_tools_version
get_logs
upload_logs
clean
