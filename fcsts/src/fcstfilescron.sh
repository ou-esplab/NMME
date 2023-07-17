#!/bin/bash
set -xve

execDIR=/home/kpegion/projects/SubX/fcsts/src/
prog=filetransfer2web.sh
fcstdate=$(date +%Y%m)

cd $execDIR
./${prog} ${fcstdate} >& fcstfiles${fcstdate}.log
