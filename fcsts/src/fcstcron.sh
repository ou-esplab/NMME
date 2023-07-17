#!/bin/bash
set -xve

hostsub=$(echo $HOSTNAME | cut -c 1-5)
echo $hostsub

execDIR=/home/kpegion/projects/NMME/fcsts/src/
prog=makefcsts.sh
fcstdate=$(date +%Y%m)
cd $execDIR
./${prog} ${fcstdate} &> fcst.log

