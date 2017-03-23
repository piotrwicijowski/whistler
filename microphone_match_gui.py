#!/usr/bin/python2

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys
import os
from PyQt5.QtWidgets import (QApplication,
        QWidget,
        QPushButton,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QSizePolicy,
        QCheckBox,
        QListWidget,
        QListWidgetItem,
        QProgressBar)
from PyQt5.QtCore import (QCoreApplication, QThread, QBasicTimer)
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
        self.result = self.matcher.recordAndMatch2()

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(400,50)
        self.move(400,600)
        self.setWindowTitle('Swing.azm')

        self.continuousMatching = True
        self.threadInterrupter = {'interrupted':False}
        self.continuousMatcher = microphone_match.ContinuousMatcher(self.threadInterrupter)
        self.matcherThread = RecorderMatcherThread(self.continuousMatcher)
        self.matcherThread.finished.connect(self.recordingFinished)

        self.recordButton = QPushButton('Record')
        self.recordButton.resize(self.recordButton.sizeHint())
        self.recordButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.recordButton.clicked.connect(self.recordAndMatch)

        self.resultLabel = QLabel('Ready')

        self.continuousCheckBox = QCheckBox()
        self.continuousCheckBox.setText('Continuous')
        self.continuousCheckBox.setChecked(self.continuousMatching)
        self.continuousCheckBox.stateChanged.connect(self.toggleContinuous)

        self.progress = 0.0
        self.progressBar = QProgressBar()
        self.progressTimer = QBasicTimer()

        self.recentList = []
        self.recentListWidget = QListWidget()
        self.recResHBox = QHBoxLayout()
        self.recResHBox.addWidget(self.recordButton)
        self.recResHBox.addWidget(self.resultLabel)

        self.mainVBox = QVBoxLayout()
        self.mainVBox.addLayout(self.recResHBox)
        self.mainVBox.addWidget(self.continuousCheckBox)
        self.mainVBox.addWidget(self.recentListWidget)
        self.mainVBox.addWidget(self.progressBar)
        # self.mainVBox.addStretch(1)
        self.setLayout(self.mainVBox)
        self.show()

    def interruptRecording(self):
        self.threadInterrupter['interrupted'] = True

    def recordAndMatch(self):
        self.threadInterrupter['interrupted'] = False
        self.recordButton.setText('Recording')
        self.progress = 0.0
        self.progressBar.setValue(0)
        self.progressTimer.start(100,self)
        self.matcherThread.start()
        self.recordButton.clicked.disconnect()
        self.recordButton.clicked.connect(self.interruptRecording)

    def recordingFinished(self):
        currentResult = self.matcherThread.result
        self.resultLabel.setText(currentResult)
        if(len(self.recentList) == 0 or self.recentList[-1] != currentResult):
            self.recentList.append(currentResult)
            self.recentListWidget.addItem(QListWidgetItem(currentResult))
        self.progressBar.setValue(100)
        self.progress = 100.0
        self.progressTimer.stop()
        if(self.continuousMatching and not self.threadInterrupter['interrupted']):
            self.recordAndMatch()
        else:
            self.recordButton.setText('Record')
            self.recordButton.clicked.disconnect()
            self.recordButton.clicked.connect(self.recordAndMatch)

    def timerEvent(self, e):
        if self.progress >= 100:
            self.progressTimer.stop()
            return
        self.progress = self.progress + 1/3.0
        self.progressBar.setValue(self.progress)

    def toggleContinuous(self):
        self.continuousMatching = self.continuousCheckBox.isChecked()
        self.continuousCheckBox.setChecked(self.continuousMatching)

if __name__ == '__main__':
    main(sys.argv)
