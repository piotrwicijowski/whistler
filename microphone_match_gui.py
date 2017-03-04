#!/usr/bin/python2

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy)
from PyQt5.QtCore import (QCoreApplication, QThread)
import microphone_match

def main(argv):
    app = QApplication(argv)
    w = MainWindow()
    sys.exit(app.exec_())

class RecorderMatcherThread(QThread):
    def __init__(self, matcher):
        super(self.__class__, self).__init__()
        self.matcher = matcher

    def __del__(self):
        self.wait()

    def run(self):
        # database_file_path = QApplication.instance().arguments()[1] if len(QApplication.instance().arguments())>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'fpdbase.pklz')
        # microphone_match.recordAndMatch(database_file_path)
        # self.recordButton.setText('Record')
        self.result = self.matcher.recordAndMatch()

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(400,50)
        self.move(400,600)
        self.setWindowTitle('Swingzam')

        self.continuousMatcher = microphone_match.ContinuousMatcher()
        self.matcherThread = RecorderMatcherThread(self.continuousMatcher)
        self.matcherThread.finished.connect(self.recordingFinished)

        self.recordButton = QPushButton('Record')
        self.recordButton.resize(self.recordButton.sizeHint())
        self.recordButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.recordButton.clicked.connect(self.recordAndMatch)

        self.resultLabel = QLabel('Ready')

        self.recResHBox = QHBoxLayout()
        self.recResHBox.addWidget(self.recordButton)
        self.recResHBox.addWidget(self.resultLabel)

        self.mainVBox = QVBoxLayout()
        self.mainVBox.addLayout(self.recResHBox)
        self.mainVBox.addStretch(1)
        self.setLayout(self.mainVBox)
        self.show()

    def recordAndMatch(self):
        self.recordButton.setText('Recording')
        self.matcherThread.start()

    def recordingFinished(self):
        self.resultLabel.setText(self.matcherThread.result)
        self.recordButton.setText('Record')

if __name__ == '__main__':
    main(sys.argv)
