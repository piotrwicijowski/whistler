#!/usr/bin/python2
# -*- coding: utf-8 -*-

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys
import os
from PyQt5.QtWidgets import (
        QApplication,
        QWidget,
        QPushButton,
        QVBoxLayout,
        QHBoxLayout,
        QFormLayout,
        QLabel,
        QSizePolicy,
        QCheckBox,
        QListWidget,
        QListWidgetItem,
        QLineEdit,
        QMainWindow,
        QAction,
        QProgressBar,
        QDialog,
        QDialogButtonBox
        )
from PyQt5.QtGui import (
        QIcon
        )
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

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(400,50)
        self.move(400,600)
        self.setWindowTitle('Whistler')

        self.centralWidget = QWidget(self)
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

        # self.continuousCheckBox = QCheckBox()
        # self.continuousCheckBox.setText('Continuous')
        # self.continuousCheckBox.setChecked(self.continuousMatching)
        # self.continuousCheckBox.stateChanged.connect(self.toggleContinuous)

        self.progress = 0.0
        self.progressBar = QProgressBar()
        self.progressTimer = QBasicTimer()

        self.recentList = []
        self.recentListWidget = QListWidget()

        self.optionsHBox = QHBoxLayout()
        # self.optionsHBox.addWidget(self.continuousCheckBox)

        self.recResHBox = QHBoxLayout()
        self.recResHBox.addWidget(self.recordButton)
        self.recResHBox.addWidget(self.resultLabel)

        self.mainVBox = QVBoxLayout()
        self.mainVBox.addLayout(self.recResHBox)
        self.mainVBox.addLayout(self.optionsHBox)
        self.mainVBox.addWidget(self.recentListWidget)
        self.mainVBox.addWidget(self.progressBar)
        # self.mainVBox.addStretch(1)
        self.centralWidget.setLayout(self.mainVBox)
        self.setCentralWidget(self.centralWidget)
        self.setupMenuBar()
        self.show()

    def setupMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Plik')
        settingsMenu = menubar.addMenu('&Ustawienia')

        exitAction = QAction(QIcon.fromTheme('application-exit'), u'&Wyjście', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Zamknij program')
        exitAction.triggered.connect(QApplication.quit)

        audioSettingsAction = QAction(QIcon.fromTheme('gnome-settings'), u'Ustawienia &nagrywania', self)
        audioSettingsAction.setShortcut('Ctrl+Shift+R')
        audioSettingsAction.setStatusTip(u'Zmień ustawienia nagrywania')
        audioSettingsAction.triggered.connect(self.openAudioSettings)

        fileMenu.addAction(exitAction)
        settingsMenu.addAction(audioSettingsAction)

    def openAudioSettings(self, newValue):
        settingsDialog = QDialog(self)

        audioDeviceLabel = QLabel()
        audioDeviceLabel.setText(u'Urządzenie audio:')
        audioDeviceLineEdit = QLineEdit()
        audioDeviceLineEdit.setText(self.continuousMatcher.FFMpegDevice)
        # audioDeviceLineEdit.textEdited.connect(self.changeFFMpegDevice)

        audioInputLabel = QLabel()
        audioInputLabel.setText(u'Wejście audio:')
        audioInputLineEdit = QLineEdit()
        audioInputLineEdit.setText(self.continuousMatcher.FFMpegInput)
        # audioInputLineEdit.textEdited.connect(self.changeFFMpegInput)

        dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogButtons.accepted.connect(settingsDialog.accept)
        dialogButtons.rejected.connect(settingsDialog.reject)

        settingsFormLayout = QFormLayout()
        settingsFormLayout.addRow(audioDeviceLabel, audioDeviceLineEdit)
        settingsFormLayout.addRow(audioInputLabel, audioInputLineEdit)

        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(settingsFormLayout)
        settingsLayout.addWidget(dialogButtons)
        settingsDialog.setLayout(settingsLayout)

        if settingsDialog.exec_():
            self.changeFFMpegDevice(audioDeviceLineEdit.text())
            self.changeFFMpegInput(audioInputLineEdit.text())

    def changeFFMpegDevice(self, newValue):
        self.continuousMatcher.FFMpegDevice = newValue
        print(newValue)

    def changeFFMpegInput(self, newValue):
        self.continuousMatcher.FFMpegInput = newValue
        print(newValue)

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
