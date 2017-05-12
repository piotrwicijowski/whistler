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
import locale
os_encoding = locale.getpreferredencoding()

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
        # self.args = docopt.docopt(audfprint.USAGE, version=audfprint.__version__, argv=['match'] + sys.argv[1:])
        self.args = docopt.docopt(audfprint.USAGE, version=audfprint.__version__, argv=sys.argv[1:])
        if getattr(sys, 'frozen', False):
            self.applicationPath = os.path.dirname(sys.executable)
        elif __file__:
            self.applicationPath = os.path.dirname(os.path.abspath(__file__))
        # if not self.args['--dbase'] :
        #     self.args['--dbase'] = os.path.join(self.applicationPath,'fpdbase.pklz')
        self.configPath = os.path.join(self.applicationPath,'config.ini')

        if not os.path.isfile(self.configPath):
            self.initSetting()

        self.settings = QSettings(self.configPath,QSettings.IniFormat)
        self.readSettings()

        self.matcher = audfprint.setup_matcher(self.args)
        self.analyzer = audfprint.setup_analyzer(self.args)
        self.openDatabaseDirectory()
        fullFingerprintPath = os.path.join(self.applicationPath, self.databaseDirectoryPath, self.databaseFingerprintFile)
        self.hash_tab = hash_table.HashTable(fullFingerprintPath)
        self.thread = thread

    def scanDirectory(self):
        fullDatabaseDirectoryPath = os.path.join(self.applicationPath, self.databaseDirectoryPath)
        if hasattr(self, 'hash_tab') and self.hash_tab:
            del self.hash_tab
        self.hash_tab = hash_table.HashTable(
            hashbits=int(self.args['--hashbits']),
            depth=int(self.args['--bucketsize']),
            maxtime=(1 << int(self.args['--maxtimebits'])))

        audioFiles = [os.path.join(self.databaseDirectoryPath, f) for f
                      in os.listdir(fullDatabaseDirectoryPath)
                      if os.path.isfile(os.path.join(fullDatabaseDirectoryPath,f))
                      and os.path.splitext(f)[1]=='.mp3']
        for filename in audioFiles:
            self.analyzer.ingest(self.hash_tab, str(filename))
        if self.hash_tab and self.hash_tab.dirty:
            fullFingerprintPath = os.path.join(self.applicationPath, self.databaseDirectoryPath, self.databaseFingerprintFile)
            self.hash_tab.save(fullFingerprintPath)

    def changeDatabaseDirectory(self, dirPath):
        self.databaseDirectoryPath = os.path.relpath(dirPath, self.applicationPath)
        self.settings.beginGroup('database')
        self.settings.setValue('directoryPath', self.databaseDirectoryPath)
        self.settings.endGroup()

    def openDatabaseDirectory(self):
        fullDatabaseDirectoryPath = os.path.join(self.applicationPath, self.databaseDirectoryPath)
        databaseFiles = [f for f
                         in os.listdir(fullDatabaseDirectoryPath)
                         if os.path.isfile(os.path.join(fullDatabaseDirectoryPath,f))
                         and os.path.splitext(f)[1]=='.pklz']
        if not databaseFiles:
            self.settings.beginGroup('database')
            self.settings.setValue('fingerprintFile', 'fpdbase.pklz')
            self.databaseFingerprintFile = 'fpdbase.pklz'
            self.settings.endGroup()
            self.scanDirectory()
        elif (self.databaseFingerprintFile not in databaseFiles):
            self.settings.beginGroup('database')
            self.settings.setValue('fingerprintFile', databaseFiles[0])
            self.databaseFingerprintFile = databaseFiles[0]
            self.settings.endGroup()

    def recordAndMatch2(self):
        FFmpegArgs = {'FFMPEG_BIN' : self.FFMpegBin.encode(os_encoding), 'FFMPEG_AUDIO_DEVICE' : self.FFMpegDevice.encode(os_encoding), 'FFMPEG_INPUT': self.FFMpegInput.encode(os_encoding)}
        return self.matcher.file_match_to_msgs(self.analyzer, self.hash_tab, FFmpegArgs, 0, self.thread)[0]
    
    def initSetting(self):
        settings = QSettings(self.configPath,QSettings.IniFormat)
        settings.beginGroup('database')
        databaseDirectoryPath = os.path.join(self.applicationPath,'..','files')
        databaseDirectoryPath = os.path.realpath(databaseDirectoryPath)
        databaseDirectoryPath = os.path.relpath(databaseDirectoryPath, self.applicationPath)
        settings.setValue('directoryPath', databaseDirectoryPath)
        settings.setValue('fingerprintFile', 'fpdbase.pklz')
        settings.endGroup()
        settings.beginGroup('FFMpeg')
        settings.setValue('bin', FFMPEG_BIN)
        settings.setValue('device', FFMPEG_AUDIO_DEVICE)
        settings.setValue('input', '\'' + FFMPEG_INPUT + '\'' )
        settings.endGroup()
        settings.beginGroup('args')
        settings.setValue('--bucketsize'        ,self.args['--bucketsize'       ])
        settings.setValue('--continue-on-error' ,self.args['--continue-on-error'])
        settings.setValue('--dbase'             ,self.args['--dbase'            ])
        settings.setValue('--density'           ,self.args['--density'          ])
        settings.setValue('--exact-count'       ,self.args['--exact-count'      ])
        settings.setValue('--fanout'            ,self.args['--fanout'           ])
        settings.setValue('--find-time-range'   ,self.args['--find-time-range'  ])
        settings.setValue('--freq-sd'           ,self.args['--freq-sd'          ])
        settings.setValue('--hashbits'          ,self.args['--hashbits'         ])
        settings.setValue('--help'              ,self.args['--help'             ])
        settings.setValue('--illustrate'        ,self.args['--illustrate'       ])
        settings.setValue('--illustrate-hpf'    ,self.args['--illustrate-hpf'   ])
        settings.setValue('--list'              ,self.args['--list'             ])
        settings.setValue('--match-win'         ,self.args['--match-win'        ])
        settings.setValue('--max-matches'       ,self.args['--max-matches'      ])
        settings.setValue('--maxtime'           ,self.args['--maxtime'          ])
        settings.setValue('--maxtimebits'       ,self.args['--maxtimebits'      ])
        settings.setValue('--min-count'         ,self.args['--min-count'        ])
        settings.setValue('--ncores'            ,self.args['--ncores'           ])
        settings.setValue('--opfile'            ,self.args['--opfile'           ])
        settings.setValue('--pks-per-frame'     ,self.args['--pks-per-frame'    ])
        settings.setValue('--precompdir'        ,self.args['--precompdir'       ])
        settings.setValue('--precompute-peaks'  ,self.args['--precompute-peaks' ])
        settings.setValue('--samplerate'        ,self.args['--samplerate'       ])
        settings.setValue('--search-depth'      ,self.args['--search-depth'     ])
        settings.setValue('--shifts'            ,self.args['--shifts'           ])
        settings.setValue('--skip-existing'     ,self.args['--skip-existing'    ])
        settings.setValue('--sortbytime'        ,self.args['--sortbytime'       ])
        settings.setValue('--time-quantile'     ,self.args['--time-quantile'    ])
        settings.setValue('--verbose'           ,self.args['--verbose'          ])
        settings.setValue('--version'           ,self.args['--version'          ])
        settings.setValue('--wavdir'            ,self.args['--wavdir'           ])
        settings.setValue('--wavext'            ,self.args['--wavext'           ])
        settings.setValue('add'                 ,self.args['add'                ])
        settings.setValue('list'                ,self.args['list'               ])
        settings.setValue('match'               ,self.args['match'              ])
        settings.setValue('merge'               ,self.args['merge'              ])
        settings.setValue('new'                 ,self.args['new'                ])
        settings.setValue('newmerge'            ,self.args['newmerge'           ])
        settings.setValue('precompute'          ,self.args['precompute'         ])
        settings.setValue('remove'              ,self.args['remove'             ])
        settings.endGroup()
        del settings

    def readSettings(self):
        self.settings.beginGroup('database')
        self.databaseDirectoryPath = self.settings.value('directoryPath')
        self.databaseFingerprintFile = self.settings.value('fingerprintFile')
        self.settings.endGroup()
        self.settings.beginGroup('FFMpeg')
        self.FFMpegBin    = self.settings.value('bin')
        self.FFMpegDevice = self.settings.value('device')
        self.FFMpegInput  = self.settings.value('input')
        self.FFMpegInput  = self.FFMpegInput.strip('\'')
        self.settings.endGroup()
        self.settings.beginGroup('args')
        self.args['--bucketsize'       ] = self.settings.value('--bucketsize'        , type=int   )
        self.args['--continue-on-error'] = self.settings.value('--continue-on-error' , type=bool  )
        self.args['--dbase'            ] = self.settings.value('--dbase'             , type=str   )
        self.args['--density'          ] = self.settings.value('--density'           , type=float )
        self.args['--exact-count'      ] = self.settings.value('--exact-count'       , type=bool  )
        self.args['--fanout'           ] = self.settings.value('--fanout'            , type=int   )
        self.args['--find-time-range'  ] = self.settings.value('--find-time-range'   , type=bool  )
        self.args['--freq-sd'          ] = self.settings.value('--freq-sd'           , type=float )
        self.args['--hashbits'         ] = self.settings.value('--hashbits'          , type=int   )
        self.args['--help'             ] = self.settings.value('--help'              , type=bool  )
        self.args['--illustrate'       ] = self.settings.value('--illustrate'        , type=bool  )
        self.args['--illustrate-hpf'   ] = self.settings.value('--illustrate-hpf'    , type=bool  )
        self.args['--list'             ] = self.settings.value('--list'              , type=bool  )
        self.args['--match-win'        ] = self.settings.value('--match-win'         , type=int   )
        self.args['--max-matches'      ] = self.settings.value('--max-matches'       , type=int   )
        self.args['--maxtime'          ] = self.settings.value('--maxtime'           , type=int   )
        self.args['--maxtimebits'      ] = self.settings.value('--maxtimebits'       )
        if self.args["--maxtimebits"]:
            self.args["--maxtimebits"] = int(self.args["--maxtimebits"])
        else:
            self.args["--maxtimebits"] = hash_table._bitsfor(int(self.args["--maxtime"]))
        self.args['--min-count'        ] = self.settings.value('--min-count'         , type=int   )
        self.args['--ncores'           ] = self.settings.value('--ncores'            , type=int   )
        self.args['--opfile'           ] = self.settings.value('--opfile'            , type=str   )
        self.args['--pks-per-frame'    ] = self.settings.value('--pks-per-frame'     , type=int   )
        self.args['--precompdir'       ] = self.settings.value('--precompdir'        , type=str   )
        self.args['--precompute-peaks' ] = self.settings.value('--precompute-peaks'  , type=bool  )
        self.args['--samplerate'       ] = self.settings.value('--samplerate'        , type=int   )
        self.args['--search-depth'     ] = self.settings.value('--search-depth'      , type=int   )
        self.args['--shifts'           ] = self.settings.value('--shifts'            , type=int   )
        self.args['--skip-existing'    ] = self.settings.value('--skip-existing'     , type=bool  )
        self.args['--sortbytime'       ] = self.settings.value('--sortbytime'        , type=bool  )
        self.args['--time-quantile'    ] = self.settings.value('--time-quantile'     , type=float )
        self.args['--verbose'          ] = self.settings.value('--verbose'           , type=str   )
        self.args['--version'          ] = self.settings.value('--version'           , type=bool  )
        self.args['--wavdir'           ] = self.settings.value('--wavdir'            , type=str   )
        self.args['--wavext'           ] = self.settings.value('--wavext'            , type=str   )
        self.args['add'                ] = self.settings.value('add'                 , type=bool  )
        self.args['list'               ] = self.settings.value('list'                , type=bool  )
        self.args['match'              ] = self.settings.value('match'               , type=bool  )
        self.args['merge'              ] = self.settings.value('merge'               , type=bool  )
        self.args['new'                ] = self.settings.value('new'                 , type=bool  )
        self.args['newmerge'           ] = self.settings.value('newmerge'            , type=bool  )
        self.args['precompute'         ] = self.settings.value('precompute'          , type=bool  )
        self.args['remove'             ] = self.settings.value('remove'              , type=bool  )
        self.settings.endGroup()

    def saveSettings(self):
        self.settings.beginGroup('database')
        self.settings.setValue('directoryPath', self.databaseDirectoryPath)
        self.settings.setValue('fingerprintFile', self.databaseFingerprintFile)
        self.settings.endGroup()
        self.settings.beginGroup('FFMpeg')
        self.settings.setValue('bin', self.FFMpegBin)
        self.settings.setValue('device', self.FFMpegDevice)
        self.settings.setValue('input', '\'' + self.FFMpegInput + '\'' )
        self.settings.endGroup()
        self.settings.beginGroup('args')
        self.settings.setValue('--bucketsize'        ,self.args['--bucketsize'       ])
        self.settings.setValue('--continue-on-error' ,self.args['--continue-on-error'])
        self.settings.setValue('--dbase'             ,self.args['--dbase'            ])
        self.settings.setValue('--density'           ,self.args['--density'          ])
        self.settings.setValue('--exact-count'       ,self.args['--exact-count'      ])
        self.settings.setValue('--fanout'            ,self.args['--fanout'           ])
        self.settings.setValue('--find-time-range'   ,self.args['--find-time-range'  ])
        self.settings.setValue('--freq-sd'           ,self.args['--freq-sd'          ])
        self.settings.setValue('--hashbits'          ,self.args['--hashbits'         ])
        self.settings.setValue('--help'              ,self.args['--help'             ])
        self.settings.setValue('--illustrate'        ,self.args['--illustrate'       ])
        self.settings.setValue('--illustrate-hpf'    ,self.args['--illustrate-hpf'   ])
        self.settings.setValue('--list'              ,self.args['--list'             ])
        self.settings.setValue('--match-win'         ,self.args['--match-win'        ])
        self.settings.setValue('--max-matches'       ,self.args['--max-matches'      ])
        self.settings.setValue('--maxtime'           ,self.args['--maxtime'          ])
        self.settings.setValue('--maxtimebits'       ,self.args['--maxtimebits'      ])
        self.settings.setValue('--min-count'         ,self.args['--min-count'        ])
        self.settings.setValue('--ncores'            ,self.args['--ncores'           ])
        self.settings.setValue('--opfile'            ,self.args['--opfile'           ])
        self.settings.setValue('--pks-per-frame'     ,self.args['--pks-per-frame'    ])
        self.settings.setValue('--precompdir'        ,self.args['--precompdir'       ])
        self.settings.setValue('--precompute-peaks'  ,self.args['--precompute-peaks' ])
        self.settings.setValue('--samplerate'        ,self.args['--samplerate'       ])
        self.settings.setValue('--search-depth'      ,self.args['--search-depth'     ])
        self.settings.setValue('--shifts'            ,self.args['--shifts'           ])
        self.settings.setValue('--skip-existing'     ,self.args['--skip-existing'    ])
        self.settings.setValue('--sortbytime'        ,self.args['--sortbytime'       ])
        self.settings.setValue('--time-quantile'     ,self.args['--time-quantile'    ])
        self.settings.setValue('--verbose'           ,self.args['--verbose'          ])
        self.settings.setValue('--version'           ,self.args['--version'          ])
        self.settings.setValue('--wavdir'            ,self.args['--wavdir'           ])
        self.settings.setValue('--wavext'            ,self.args['--wavext'           ])
        self.settings.setValue('add'                 ,self.args['add'                ])
        self.settings.setValue('list'                ,self.args['list'               ])
        self.settings.setValue('match'               ,self.args['match'              ])
        self.settings.setValue('merge'               ,self.args['merge'              ])
        self.settings.setValue('new'                 ,self.args['new'                ])
        self.settings.setValue('newmerge'            ,self.args['newmerge'           ])
        self.settings.setValue('precompute'          ,self.args['precompute'         ])
        self.settings.setValue('remove'              ,self.args['remove'             ])
        self.settings.endGroup()

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
