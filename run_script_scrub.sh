#!/bin/bash
PATH=/home/crosby/bin:/home/crosby/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

cd /home/crosby/Documents/SkagitOperational

DATE=`date '+%Y-%m-%d %H:%M:%S'`

#echo $DATE >> davis_scrub.log

python scrub_davis_met.py #>> davis_scrub.log


