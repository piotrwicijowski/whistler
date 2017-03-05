#!/usr/bin/python

from __future__ import print_function

import os
import sys
from sys import platform
import audfprint
import hash_table
import audfprint_match
import tempfile
import subprocess
import docopt

if platform == "linux" or platform == "linux2":
    FFMPEG_BIN = "ffmpeg"     # on Linux
    FFMPEG_AUDIO_DEVICE = "alsa"
    # FFMPEG_AUDIO_DEVICE = "pulse"
elif platform == "win32":
    FFMPEG_BIN = "ffmpeg.exe" # on Windows
    FFMPEG_AUDIO_DEVICE = "dsound"
elif platform == "darwin":
    FFMPEG_BIN = "ffmpeg"     # on OSX
    FFMPEG_AUDIO_DEVICE = "dsound"

class ContinuousMatcher(object):
    def __init__(self):
        self.args = docopt.docopt(audfprint.USAGE, version=audfprint.__version__, argv=['match'] + sys.argv[1:])
        if not self.args['--dbase'] :
            self.args['--dbase'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),'fpdbase.pklz')
        self.matcher = audfprint.setup_matcher(self.args)
        self.hash_tab = hash_table.HashTable(self.args['--dbase'])
        self.analyzer = audfprint.setup_analyzer(self.args)

    def recordAndMatch(self):
        with tempfile.NamedTemporaryFile(suffix='.mp3') as recording_file:
            command = [FFMPEG_BIN,
                    '-f', FFMPEG_AUDIO_DEVICE,
                    '-i', 'pulse',
                    # '-i', 'default',
                    '-y',
                    '-t', '00:30',
                    recording_file.name]
            recording_process = subprocess.Popen(command,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            recording_process.wait()
            return self.matcher.file_match_to_msgs(self.analyzer, self.hash_tab, recording_file.name, 0)[0]
            # audfprint.main(['audfprint.py', 'match',
            #     '--dbase',
            #     self.database_file_path,
            #     recording_file.name])

def main(argv):
    database_file_path = argv[1] if len(argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'fpdbase.pklz')
    if os.path.isfile(database_file_path) and os.access(database_file_path, os.R_OK):
        print('Recording, please wait...')
        matcher = ContinuousMatcher()
        print(matcher.recordAndMatch())
    else:
        print('The database file is missing or is not readable')
    input('Press Enter to exit')


if __name__ == "__main__":
    main(sys.argv)
