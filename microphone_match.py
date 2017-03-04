#!/usr/bin/python2

from __future__ import print_function

import os
import sys
from sys import platform
import audfprint
import tempfile
import subprocess

if platform == "linux" or platform == "linux2":
    FFMPEG_BIN = "ffmpeg"     # on Linux
    FFMPEG_AUDIO_DEVICE = "pulse"
elif platform == "win32":
    FFMPEG_BIN = "ffmpeg.exe" # on Windows
    FFMPEG_AUDIO_DEVICE = "dsound"
elif platform == "darwin":
    FFMPEG_BIN = "ffmpeg"     # on OSX
    FFMPEG_AUDIO_DEVICE = "dsound"

def main(argv):
    database_file_path = argv[1] if len(argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'fpdbase.pklz')
    if os.path.isfile(database_file_path) and os.access(database_file_path, os.R_OK):
        with tempfile.NamedTemporaryFile(suffix='.mp3') as recording_file:
            command = [FFMPEG_BIN,
                    '-f', FFMPEG_AUDIO_DEVICE,
                    '-i', 'default',
                    '-y',
                    '-t', '00:30',
                    recording_file.name]
            recording_process = subprocess.Popen(command,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print('recording, please wait...')
            recording_process.wait()
            audfprint.main(['audfprint.py', 'match',
                '--dbase',
                database_file_path,
                recording_file.name])
            raw_input('Press Enter to exit')
    else:
        print('The database file is missing or is not readable')

if __name__ == "__main__":
    main(sys.argv)
