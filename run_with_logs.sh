#!/bin/sh
NOW=$(date +"%Y-%m-%d_%H-%M-%S")
python2 $@ > ${NOW}_log.txt 2> ${NOW}_err.txt
