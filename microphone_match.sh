#!/bin/bash
filename=$(mktemp --suffix=.mp3)
ffmpeg -f pulse -i default -y -t 00:30 $filename
python2 /home/stryjan/src/audfprint/audfprint.py match --dbase /home/stryjan/Swing/FingerprintTest/fpdbase.pklz $filename
rm $filename
read -p "Press any key to close"
