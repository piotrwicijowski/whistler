#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import time
import sys
from sys import platform
import audfprint
import hash_table
import tempfile
import subprocess
import docopt
import codecs
from PyQt5.QtCore import QSettings

if platform == "linux" or platform == "linux2":
    FFMPEG_BIN = "ffmpeg"     # on Linux
    FFMPEG_AUDIO_DEVICE = "pulse"
    FFMPEG_INPUT = "default"
elif platform == "win32":
    FFMPEG_BIN = "ffmpeg.exe" # on Windows
    FFMPEG_AUDIO_DEVICE = "dshow"
    FFMPEG_INPUT = u"audio=Mikrofon (Urz\u0105dzenie zgodne ze "
# elif platform == "darwin":
#     FFMPEG_BIN = "ffmpeg"     # on OSX
#     FFMPEG_AUDIO_DEVICE = "dsound"

class ContinuousMatcher(object):
    def __init__(self, thread):
        self.args = docopt.docopt(audfprint.USAGE, version=audfprint.__version__, argv=['match'] + sys.argv[1:])
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(os.path.abspath(__file__))
        if not self.args['--dbase'] :
            self.args['--dbase'] = os.path.join(application_path,'fpdbase.pklz')
        configPath = os.path.join(application_path,'config.ini')

        # config = SafeConfigParser()
        if not os.path.isfile(configPath):
            settings = QSettings(configPath,QSettings.IniFormat)
            settings.beginGroup('FFMpeg')
            settings.setValue('bin', FFMPEG_BIN)
            settings.setValue('device', FFMPEG_AUDIO_DEVICE)
            settings.setValue('input', '\'' + FFMPEG_INPUT + '\'' )
            settings.endGroup()
            del settings

            # config.add_section('FFMpeg')
            # self.FFMpegBin    = config.set('FFMpeg', 'bin', FFMPEG_BIN)
            # self.FFMpegDevice = config.set('FFMpeg', 'device', FFMPEG_AUDIO_DEVICE)
            # self.FFMpegInput  = config.set('FFMpeg', 'input', '\'' + FFMPEG_INPUT + '\'' )
            # with codecs.open(configPath, 'wb+', encoding='utf-8') as configFile:
            #     config.write(configFile)
        # with codecs.open(configPath, 'r', encoding='utf-8') as f:
        #     config.readfp(f)
        settings = QSettings(configPath,QSettings.IniFormat)
        settings.beginGroup('FFMpeg')
        self.FFMpegBin    = settings.value('bin')
        self.FFMpegDevice = settings.value('device')
        self.FFMpegInput  = settings.value('input')
        self.FFMpegInput  = self.FFMpegInput.strip('\'')
        print(repr( self.FFMpegInput ))
        self.FFMpegInput  = self.FFMpegInput.encode('windows-1250')
        print(repr( self.FFMpegInput ))
        print(repr(u"audio=Mikrofon (Urz\u0105dzenie zgodne ze ".encode('windows-1250')))
        self.matcher = audfprint.setup_matcher(self.args)
        self.hash_tab = hash_table.HashTable(self.args['--dbase'])
        self.analyzer = audfprint.setup_analyzer(self.args)
        self.thread = thread
    def recordAndMatch2(self):
        FFmpegArgs = {'FFMPEG_AUDIO_DEVICE' : self.FFMpegDevice, 'FFMPEG_INPUT': self.FFMpegInput}
        return self.matcher.file_match_to_msgs(self.analyzer, self.hash_tab, FFmpegArgs, 0, self.thread)[0]
    def recordAndMatch(self):
        recording_file = tempfile.NamedTemporaryFile(suffix='.mp3',delete=False)
        try:
            recording_file.close()
            command = [self.FFMpegBin,
                    '-f', self.FFMpegDevice,
                    '-i', self.FFMpegInput,
                    '-y',
                    '-t', '00:30',
                    recording_file.name]
            recording_process = subprocess.Popen(command,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            recording_process.communicate()
            recording_process.wait()
            return self.matcher.file_match_to_msgs(self.analyzer, self.hash_tab, recording_file.name, 0)[0]
        except Exception as e:
            print(str(e))
        finally:
            os.remove(recording_file.name)
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
