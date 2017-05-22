#!/bin/bash
NOW=$(date +"%Y-%m-%d_%H-%M-%S")
# python2 $@ > ${NOW}_log.txt 2> ${NOW}_err.txt
python2 $@ > >(tee -a ${NOW}_log.txt) 2> >(tee -a ${NOW}_err.txt >&2)
