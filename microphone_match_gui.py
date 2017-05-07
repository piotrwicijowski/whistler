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
        QTableWidget,
        QTableWidgetItem,
        QFileDialog,
        QDialogButtonBox
        )
from PyQt5.QtGui import (
        QIcon
        )
from PyQt5.QtCore import (QCoreApplication, QThread, QBasicTimer, QUrl, pyqtProperty, pyqtSlot, pyqtSignal)
from PyQt5.QtQml import (qmlRegisterType, QQmlComponent, QQmlEngine)
from PyQt5.QtQuick import (QQuickView)
from PyQt5.QtQuickWidgets import (QQuickWidget)
import locale
os_encoding = locale.getpreferredencoding()
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
        # self.continuousMatching = True
        self.continuousMatching = False
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

        runFullscreenAction = QAction(QIcon.fromTheme('fullscreen'), u'&Pełny ekran', self)
        runFullscreenAction.setShortcut('F11')
        runFullscreenAction.setStatusTip(u'Uruchom widok pełnoekranowy')
        runFullscreenAction.triggered.connect(self.runFullscreen)

        databaseManagementAction = QAction(QIcon.fromTheme('database'), u'&Baza danych', self)
        databaseManagementAction.setShortcut('Ctrl+B')
        databaseManagementAction.setStatusTip(u'Zarządzaj bazą danych')
        databaseManagementAction.triggered.connect(self.openDatabaseManagement)

        chooseDatabaseAction = QAction(QIcon.fromTheme('fileopen'), u'&Otwórz bazę danych', self)
        chooseDatabaseAction.setShortcut('Ctrl+O')
        chooseDatabaseAction.setStatusTip('Otwórz katalog zawierający bazę danych')
        chooseDatabaseAction.triggered.connect(self.chooseDatabaseDirectory)

        exitAction = QAction(QIcon.fromTheme('application-exit'), u'&Wyjście', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Zamknij program')
        exitAction.triggered.connect(QApplication.quit)

        audioSettingsAction = QAction(QIcon.fromTheme('gnome-settings'), u'Ustawienia &nagrywania', self)
        audioSettingsAction.setShortcut('Ctrl+Shift+R')
        audioSettingsAction.setStatusTip(u'Zmień ustawienia nagrywania')
        audioSettingsAction.triggered.connect(self.openAudioSettings)

        matcherSettingsAction = QAction(QIcon.fromTheme('gnome-settings'), u'Ustawienia &dopasowywania', self)
        matcherSettingsAction.setShortcut('Ctrl+Shift+M')
        matcherSettingsAction.setStatusTip(u'Zmień ustawienia dopasowywania')
        matcherSettingsAction.triggered.connect(self.openMatcherSettings)

        scannerSettingsAction = QAction(QIcon.fromTheme('gnome-settings'), u'Ustawienia &skanowania', self)
        scannerSettingsAction.setShortcut('Ctrl+Shift+S')
        scannerSettingsAction.setStatusTip(u'Zmień ustawienia skanowania')
        scannerSettingsAction.triggered.connect(self.openScannerSettings)

        fileMenu.addAction(runFullscreenAction)
        fileMenu.addAction(chooseDatabaseAction)
        fileMenu.addAction(databaseManagementAction)
        fileMenu.addAction(exitAction)
        settingsMenu.addAction(audioSettingsAction)
        settingsMenu.addAction(matcherSettingsAction)
        settingsMenu.addAction(scannerSettingsAction)

    def runFullscreen(self):
        window = QDialog(self)
        widget = QQuickWidget()
        layout = QVBoxLayout(window)
        layout.addWidget(widget)
        window.setLayout(layout)
        widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        # view = QQuickView()
        widget.setSource(QUrl('fullscreen.qml'))
        # engine = widget.engine()
        mainRootObject = widget.rootObject()
        mainRootObject.startRecording.connect(self.recordAndMatch)
        self.recordingStartedSignal.connect(mainRootObject.stateRecording)
        self.recordingFinishedSignal.connect(mainRootObject.stateReady)
        window.show()

    def openDatabaseManagement(self, newValue):
        databaseDialog = QDialog(self)

        tableHeaders = [u'Obraz',u'Artysta',u'Tytuł',u'Audio']
        databaseTable = QTableWidget()
        databaseTable.setRowCount(len(self.continuousMatcher.hash_tab.metadata))
        databaseTable.setColumnCount(len(tableHeaders))
        databaseTable.setHorizontalHeaderLabels(tableHeaders)
        for i, val in enumerate(self.continuousMatcher.hash_tab.metadata):
            artistItem = QTableWidgetItem(val["artist"])
            titleItem = QTableWidgetItem(val["title"])
            audioItem = QTableWidgetItem(self.continuousMatcher.hash_tab.names[i])
            databaseTable.setItem(i,1,artistItem)
            databaseTable.setItem(i,2,titleItem)
            databaseTable.setItem(i,3,audioItem)

        databaseTable.resizeColumnsToContents()
        databaseTable.resizeRowsToContents()

        dialogButtons = QDialogButtonBox(QDialogButtonBox.Close)
        dialogButtons.rejected.connect(databaseDialog.accept)

        databaseLayout = QVBoxLayout()
        databaseLayout.addWidget(databaseTable)
        databaseLayout.addWidget(dialogButtons)
        databaseDialog.setLayout(databaseLayout)

        databaseDialog.exec_()

    def openScannerSettings(self, newValue):
        settingsDialog = QDialog(self)

        densityLabel = QLabel()
        densityLabel.setText(u'Gęstość znaczników na sekundę')
        densityLineEdit = QLineEdit()
        densityLineEdit.setText(str(self.continuousMatcher.args['--density']))

        hashbitsLabel = QLabel()
        hashbitsLabel.setText(u'Ilość bitów na znacznik')
        hashbitsLineEdit = QLineEdit()
        hashbitsLineEdit.setText(str(self.continuousMatcher.args['--hashbits']))

        bucketsizeLabel = QLabel()
        bucketsizeLabel.setText(u'Rozmiar kubła znaczników')
        bucketsizeLineEdit = QLineEdit()
        bucketsizeLineEdit.setText(str(self.continuousMatcher.args['--bucketsize']))

        maxtimeLabel = QLabel()
        maxtimeLabel.setText(u'Maksymalny zapisany czas')
        maxtimeLineEdit = QLineEdit()
        maxtimeLineEdit.setText(str(self.continuousMatcher.args['--maxtime']))

        samplerateLabel = QLabel()
        samplerateLabel.setText(u'Częstotliwość próbkowania')
        samplerateLineEdit = QLineEdit()
        samplerateLineEdit.setText(str(self.continuousMatcher.args['--samplerate']))

        shiftsLabel = QLabel()
        shiftsLabel.setText(u'Ilość przesunięć przy liczeniu odcisków')
        shiftsLineEdit = QLineEdit()
        shiftsLineEdit.setText(str(self.continuousMatcher.args['--shifts']))

        quantileLabel = QLabel()
        quantileLabel.setText(u'Kwantyl dla extremów')
        quantileLineEdit = QLineEdit()
        quantileLineEdit.setText(str(self.continuousMatcher.args['--time-quantile']))

        frequencySDLabel = QLabel()
        frequencySDLabel.setText(u'Częstotliwość SD')
        frequencySDLineEdit = QLineEdit()
        frequencySDLineEdit.setText(str(self.continuousMatcher.args['--freq-sd']))

        fanoutLabel = QLabel()
        fanoutLabel.setText(u'Maksymalna ilość par znaczników na szczyt')
        fanoutLineEdit = QLineEdit()
        fanoutLineEdit.setText(str(self.continuousMatcher.args['--fanout']))

        pksPerFrameLabel = QLabel()
        pksPerFrameLabel.setText(u'Ilość szczytów na ramkę')
        pksPerFrameLineEdit = QLineEdit()
        pksPerFrameLineEdit.setText(str(self.continuousMatcher.args['--pks-per-frame']))

        searchDepthLabel = QLabel()
        searchDepthLabel.setText(u'Głębokość wyszukiwania')
        searchDepthLineEdit = QLineEdit()
        searchDepthLineEdit.setText(str(self.continuousMatcher.args['--search-depth']))

        dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogButtons.accepted.connect(settingsDialog.accept)
        dialogButtons.rejected.connect(settingsDialog.reject)

        settingsFormLayout = QFormLayout()
        settingsFormLayout.addRow(densityLabel   , densityLineEdit)
        settingsFormLayout.addRow(hashbitsLabel   , hashbitsLineEdit)
        settingsFormLayout.addRow(bucketsizeLabel , bucketsizeLineEdit)
        settingsFormLayout.addRow(maxtimeLabel , maxtimeLineEdit)
        settingsFormLayout.addRow(samplerateLabel , samplerateLineEdit)
        settingsFormLayout.addRow(shiftsLabel , shiftsLineEdit)
        settingsFormLayout.addRow(quantileLabel , quantileLineEdit)
        settingsFormLayout.addRow(frequencySDLabel , frequencySDLineEdit)
        settingsFormLayout.addRow(fanoutLabel , fanoutLineEdit)
        settingsFormLayout.addRow(pksPerFrameLabel , pksPerFrameLineEdit)
        settingsFormLayout.addRow(searchDepthLabel , searchDepthLineEdit)

        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(settingsFormLayout)
        settingsLayout.addWidget(dialogButtons)
        settingsDialog.setLayout(settingsLayout)

        if settingsDialog.exec_():
            self.continuousMatcher.args['--density']       = float(densityLineEdit.text())
            self.continuousMatcher.args['--hashbits']      = int(hashbitsLineEdit.text())
            self.continuousMatcher.args['--bucketsize']    = int(bucketsizeLineEdit.text())
            self.continuousMatcher.args['--maxtime']       = int(maxtimeLineEdit.text())
            self.continuousMatcher.args['--samplerate']    = int(samplerateLineEdit.text())
            self.continuousMatcher.args['--shifts']        = int(shiftsLineEdit.text())
            self.continuousMatcher.args['--time-quantile'] = float(quantileLineEdit.text())
            self.continuousMatcher.args['--freq-sd']       = float(frequencySDLineEdit.text())
            self.continuousMatcher.args['--fanout']        = int(fanoutLineEdit.text())
            self.continuousMatcher.args['--pks-per-frame'] = int(pksPerFrameLineEdit.text())
            self.continuousMatcher.args['--search-depth']  = int(searchDepthLineEdit.text())
            self.continuousMatcher.saveSettings()

    def openMatcherSettings(self, newValue):
        settingsDialog = QDialog(self)

        matchWinLabel = QLabel()
        matchWinLabel.setText(u'Maksymalne przesunięcie ramek:')
        matchWinLineEdit = QLineEdit()
        matchWinLineEdit.setText(str(self.continuousMatcher.args['--match-win']))

        minCountLabel = QLabel()
        minCountLabel.setText(u'Minimalna liczba trafień:')
        minCountLineEdit = QLineEdit()
        minCountLineEdit.setText(str(self.continuousMatcher.args['--min-count']))

        exactCountLabel = QLabel()
        exactCountLabel.setText(u'Dokładne liczenie trafień:')
        exactCountCheckBox = QCheckBox()
        exactCountCheckBox.setChecked(bool(self.continuousMatcher.args['--exact-count']))

        dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogButtons.accepted.connect(settingsDialog.accept)
        dialogButtons.rejected.connect(settingsDialog.reject)

        settingsFormLayout = QFormLayout()
        settingsFormLayout.addRow(matchWinLabel, matchWinLineEdit)
        settingsFormLayout.addRow(minCountLabel, minCountLineEdit)
        settingsFormLayout.addRow(exactCountLabel, exactCountCheckBox)

        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(settingsFormLayout)
        settingsLayout.addWidget(dialogButtons)
        settingsDialog.setLayout(settingsLayout)

        if settingsDialog.exec_():
            self.continuousMatcher.args['--match-win'] = int(matchWinLineEdit.text())
            self.continuousMatcher.args['--min-count'] = int(minCountLineEdit.text())
            self.continuousMatcher.args['--exact-count'] = exactCountCheckBox.isChecked()
            self.continuousMatcher.saveSettings()

    def openAudioSettings(self, newValue):
        settingsDialog = QDialog(self)

        audioBinLabel = QLabel()
        audioBinLabel.setText(u'Ścieżka do ffmpeg:')
        audioBinLineEdit = QLineEdit()
        audioBinLineEdit.setText(self.continuousMatcher.FFMpegBin)

        audioDeviceLabel = QLabel()
        audioDeviceLabel.setText(u'Urządzenie audio:')
        audioDeviceLineEdit = QLineEdit()
        audioDeviceLineEdit.setText(self.continuousMatcher.FFMpegDevice)

        audioInputLabel = QLabel()
        audioInputLabel.setText(u'Wejście audio:')
        audioInputLineEdit = QLineEdit()
        audioInputLineEdit.setText(self.continuousMatcher.FFMpegInput)

        dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogButtons.accepted.connect(settingsDialog.accept)
        dialogButtons.rejected.connect(settingsDialog.reject)

        settingsFormLayout = QFormLayout()
        settingsFormLayout.addRow(audioBinLabel, audioBinLineEdit)
        settingsFormLayout.addRow(audioDeviceLabel, audioDeviceLineEdit)
        settingsFormLayout.addRow(audioInputLabel, audioInputLineEdit)

        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(settingsFormLayout)
        settingsLayout.addWidget(dialogButtons)
        settingsDialog.setLayout(settingsLayout)

        if settingsDialog.exec_():
            self.continuousMatcher.FFMpegBin = unicode(audioBinLineEdit.text())
            self.continuousMatcher.FFMpegDevice = unicode(audioDeviceLineEdit.text())
            self.continuousMatcher.FFMpegInput = unicode(audioInputLineEdit.text())
            self.continuousMatcher.saveSettings()

    def chooseDatabaseDirectory(self):
        prevDirPath = os.path.join(self.continuousMatcher.applicationPath, self.continuousMatcher.databaseDirectoryPath)
        prevDirPath = os.path.normpath(prevDirPath)
        print(prevDirPath)
        dirPath = QFileDialog.getExistingDirectory(self, u'Wybierz katalog z bazą danych', prevDirPath, QFileDialog.ShowDirsOnly )
        if dirPath:
            self.continuousMatcher.changeDatabaseDirectory(dirPath)
            self.continuousMatcher.openDatabaseDirectory()

    def interruptRecording(self):
        self.threadInterrupter['interrupted'] = True

    recordingStartedSignal = pyqtSignal()
    def recordAndMatch(self):
        self.threadInterrupter['interrupted'] = False
        self.recordButton.setText('Recording')
        self.progress = 0.0
        self.progressBar.setValue(0)
        self.progressTimer.start(100,self)
        self.matcherThread.start()
        self.recordButton.clicked.disconnect()
        self.recordButton.clicked.connect(self.interruptRecording)
        self.recordingStartedSignal.emit()

    recordingFinishedSignal = pyqtSignal()
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
        self.recordingFinishedSignal.emit()

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
