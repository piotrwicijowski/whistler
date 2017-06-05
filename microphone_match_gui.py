#!/usr/bin/python2
# -*- coding: utf-8 -*-

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys
from sys import platform
import os
import datetime
from PyQt5.QtWidgets import (
        QApplication,
        QWidget,
        QPushButton,
        QVBoxLayout,
        QHBoxLayout,
        QFormLayout,
        QStackedWidget,
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
        QDialogButtonBox,
        QGraphicsScene,
        QGraphicsView,
        QGraphicsPixmapItem
        )
from PyQt5.QtGui import (
        QIcon,
        QPixmap,
        QImage,
        QPalette
        )
from PyQt5.QtCore import (
        QCoreApplication,
        QThread,
        QBasicTimer,
        QUrl,
        pyqtProperty,
        pyqtSlot,
        pyqtSignal,
        Qt,
        QT_VERSION_STR
        )
from PyQt5.QtQml import (qmlRegisterType, QQmlComponent, QQmlEngine)
from PyQt5.QtQuick import (QQuickView)
from PyQt5.QtQuickWidgets import (QQuickWidget)
import locale
os_encoding = locale.getpreferredencoding()
import microphone_match
import scannerSettingsDialog
import matcherSettingsDialog
import audioSettingsDialog
import uiSettingsDialog
import re

major, minor, bugfix = QT_VERSION_STR.split('.')
major = int(major)
minor = int(minor)
bugfix = int(bugfix)
if platform == "win32" or major<5 or minor<8:
    enableQmlFullscreen = False
else:
    enableQmlFullscreen = True

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
        self.fullscreenWindow = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Whistler')

        self.stackedWidget = QStackedWidget(self)
        self.centralWidget = QWidget(self.stackedWidget)
        self.stackedWidget.addWidget(self.centralWidget)
        # self.continuousMatching = True
        self.continuousMatching = False
        self.threadInterrupter = {'interrupted':False}
        self.continuousMatcher = microphone_match.ContinuousMatcher(self.threadInterrupter)
        self.matcherThread = RecorderMatcherThread(self.continuousMatcher)
        self.matcherThread.finished.connect(self.recordingFinished)

        self.recordButton = QPushButton(u'Nagrywaj')
        self.recordButton.resize(self.recordButton.sizeHint())
        self.recordButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.recordButton.clicked.connect(self.recordAndMatch)

        self.resultLabel = QLabel()
        if self.continuousMatcher.ready:
            self.resultLabel.setText(u'Gotowy')
        else:
            self.resultLabel.setText(u'Proszę wybrać katalog z bazą danych')

        self.pictureLabel = QLabel();
        self.pictureImage = QImage("image.jpg")
        self.pictureImage = self.pictureImage.scaled(200,200,Qt.IgnoreAspectRatio,Qt.FastTransformation)
        self.pictureLabel.setAlignment( Qt.AlignRight | Qt.AlignVCenter );
        self.pictureLabel.setPixmap(QPixmap.fromImage(self.pictureImage))

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
        self.recResHBox.addWidget(self.pictureLabel)

        self.mainVBox = QVBoxLayout()
        self.mainVBox.addLayout(self.recResHBox)
        self.mainVBox.addLayout(self.optionsHBox)
        # self.mainVBox.addWidget(self.recentListWidget)
        self.mainVBox.addWidget(self.progressBar)
        # self.mainVBox.addStretch(1)
        self.centralWidget.setLayout(self.mainVBox)
        self.setCentralWidget(self.stackedWidget)
        self.runningInFullscreen = False
        self.defaultImagePath = os.path.join(self.continuousMatcher.applicationPath,'default.png')
        if enableQmlFullscreen:
            self.setupFullscreenView()
            if(self.continuousMatcher.startFullscreen):
                self.runFullscreen()
        self.setupMenuBar()
        self.show()

    def setupMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Plik')
        settingsMenu = menubar.addMenu('&Ustawienia')

        if enableQmlFullscreen:
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

        uiSettingsAction = QAction(QIcon.fromTheme('gnome-settings'), u'Ustawienia &interfejsu', self)
        uiSettingsAction.setShortcut('Ctrl+Shift+U')
        uiSettingsAction.setStatusTip(u'Zmień ustawienia interfejsu')
        uiSettingsAction.triggered.connect(self.openUiSettings)

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

        if enableQmlFullscreen:
            fileMenu.addAction(runFullscreenAction)
        fileMenu.addAction(chooseDatabaseAction)
        fileMenu.addAction(databaseManagementAction)
        fileMenu.addAction(exitAction)
        settingsMenu.addAction(uiSettingsAction)
        settingsMenu.addAction(audioSettingsAction)
        settingsMenu.addAction(matcherSettingsAction)
        settingsMenu.addAction(scannerSettingsAction)

    def setupFullscreenView(self):
            self.fullscreenWidget = QQuickWidget(self)
            self.fullscreenWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
            self.fullscreenWidget.setSource(QUrl(os.path.join(self.continuousMatcher.applicationPath,'fullscreen.qml')))
            mainRootObject = self.fullscreenWidget.rootObject()
            mainRootObject.startRecording.connect(self.recordAndMatch)
            mainRootObject.stopRecording.connect(self.interruptRecording)
            mainRootObject.closeWindow.connect(self.closeFullscreenWindow)
            self.recordingStartedSignal.connect(mainRootObject.stateRecording)
            self.recordingFinishedSignal.connect(mainRootObject.stateReady)
            self.progressChangedSignal.connect(mainRootObject.setProgress)
            self.enablePlaybackSignal.connect(mainRootObject.enablePlayback)
            self.enableAutoPlaybackSignal.connect(mainRootObject.enableAutoPlayback)
            self.enablePlaybackSignal.emit(self.continuousMatcher.enablePlayback)
            self.enableAutoPlaybackSignal.emit(self.continuousMatcher.autoPlayback)
            self.stackedWidget.addWidget(self.fullscreenWidget)

    def runFullscreen(self):
        if enableQmlFullscreen:
            if not self.runningInFullscreen:
                self.runningInFullscreen = True
                self.stackedWidget.setCurrentIndex(1)
                self.menuBar().setVisible(False)
                self.showFullScreen()
            else:
                self.runningInFullscreen = False
                self.stackedWidget.setCurrentIndex(0)
                self.menuBar().setVisible(True)
                self.showNormal()

    def closeFullscreenWindow(self):
        if enableQmlFullscreen:
            self.runningInFullscreen = False
            self.stackedWidget.setCurrentIndex(0)
            self.menuBar().setVisible(True)
            self.showNormal()

    def openDatabaseManagement(self, newValue):
        databaseDialog = QDialog(self)

        databaseTable = QTableWidget()
        self.fillDatabaseManagementTable(databaseTable)

        rescanButton = QPushButton(u'Skanuj ponownie')
        rescanButton.clicked.connect(lambda: self.rescanDatabaseAndFillTable(databaseTable))

        dialogButtons = QDialogButtonBox(QDialogButtonBox.Close)
        dialogButtons.rejected.connect(databaseDialog.accept)

        databaseLayout = QVBoxLayout()
        databaseLayout.addWidget(databaseTable)
        databaseLayout.addWidget(rescanButton)
        databaseLayout.addWidget(dialogButtons)
        databaseDialog.setLayout(databaseLayout)

        databaseDialog.exec_()

    def rescanDatabaseAndFillTable(self,table):
        self.continuousMatcher.scanDirectory()
        self.fillDatabaseManagementTable(table)

    def fillDatabaseManagementTable(self, table):
        tableHeaders = [u'Obraz',u'Artysta',u'Tytuł',u'Audio']
        table.setRowCount(0)
        table.setRowCount(len(self.continuousMatcher.hash_tab.metadata))
        table.setColumnCount(len(tableHeaders))
        table.setHorizontalHeaderLabels(tableHeaders)
        for i, val in enumerate(self.continuousMatcher.hash_tab.metadata):
            artistItem = QTableWidgetItem(val.get("artist",""))
            titleItem  = QTableWidgetItem(val.get("title",""))
            audioItem = QTableWidgetItem(self.continuousMatcher.hash_tab.names[i])
            table.setItem(i,1,artistItem)
            table.setItem(i,2,titleItem)
            table.setItem(i,3,audioItem)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    def openScannerSettings(self, newValue):
        settingsDialog = scannerSettingsDialog.ScannerSettingsDialog(self, self.continuousMatcher)
        settingsDialog.run()

    def openMatcherSettings(self, newValue):
        settingsDialog = matcherSettingsDialog.MatcherSettingsDialog(self, self.continuousMatcher)
        settingsDialog.run()

    def openUiSettings(self, newValue):
        settingsDialog = uiSettingsDialog.UiSettingDialog(self,self.continuousMatcher)
        settingsDialog.run()
        self.enablePlaybackSignal.emit(self.continuousMatcher.enablePlayback)
        self.enableAutoPlaybackSignal.emit(self.continuousMatcher.autoPlayback)

    def openAudioSettings(self, newValue):
        settingsDialog = audioSettingsDialog.AudioSettingDialog(self,self.continuousMatcher)
        settingsDialog.run()

    def chooseDatabaseDirectory(self):
        prevDirPath = os.path.join(self.continuousMatcher.applicationPath, self.continuousMatcher.databaseDirectoryPath)
        prevDirPath = os.path.normpath(prevDirPath)
        dirPath = QFileDialog.getExistingDirectory(self, u'Wybierz katalog z bazą danych', prevDirPath, QFileDialog.ShowDirsOnly )
        if dirPath:
            self.continuousMatcher.changeDatabaseDirectory(dirPath)
            self.continuousMatcher.openDatabaseDirectory()
            if self.continuousMatcher.ready:
                self.resultLabel.setText(u'Gotowy')
            else:
                self.resultLabel.setText(u'Proszę wybrać katalog z bazą danych')

    def interruptRecording(self):
        self.threadInterrupter['interrupted'] = True

    enableAutoPlaybackSignal = pyqtSignal(bool)

    enablePlaybackSignal = pyqtSignal(bool)

    recordingStartedSignal = pyqtSignal()
    def recordAndMatch(self):
        self.threadInterrupter['interrupted'] = False
        self.recordButton.setText(u'Nagrywanie')
        self.progress = 0.0
        self.progressBar.setValue(0)
        self.progressTimer.start(100,self)
        self.progressChangedSignal.emit(self.progress)
        self.matcherThread.start()
        self.recordButton.clicked.disconnect()
        self.recordButton.clicked.connect(self.interruptRecording)
        self.recordingStartedSignal.emit()

    recordingFinishedSignal = pyqtSignal(str, str, str, str)
    def recordingFinished(self):
        currentResult = self.resultTextFormatter(self.matcherThread.result)

        rawFilenameWithoutExtension = os.path.splitext(self.matcherThread.result["filename"])[0]
        filenameWithoutExtension = re.sub(r"\[.*\]","",rawFilenameWithoutExtension)
        resultAudioPath = self.matcherThread.result["filename"];

        videoExtensions = ['AVI', 'avi', 'MOV', 'mov']
        possibleVideoPaths = [os.path.normpath(os.path.join(self.continuousMatcher.databaseDirectoryPath, filenameWithoutExtension + "." + ext)) for ext in videoExtensions]
        videoPaths = [path for path in possibleVideoPaths if os.path.exists(path)]
        if len(videoPaths) > 0:
            resultVideoPath = videoPaths[0]
        else:
            resultVideoPath = ""

        imageExtensions = ['png', 'jpg', 'jpeg', 'bmp']
        possibleImagePaths = [os.path.normpath(os.path.join(self.continuousMatcher.databaseDirectoryPath, filenameWithoutExtension + "." + ext)) for ext in imageExtensions]
        imagePaths = [path for path in possibleImagePaths if os.path.exists(path)]
        if len(imagePaths) > 0:
            resultImagePath = imagePaths[0]
        else:
            resultImagePath = self.defaultImagePath

        textExtensions = ['html', 'txt']
        possibleTextPaths = [os.path.normpath(os.path.join(self.continuousMatcher.databaseDirectoryPath, filenameWithoutExtension + "." + ext)) for ext in textExtensions]
        textPaths = [path for path in possibleTextPaths if os.path.exists(path)]
        if len(textPaths) > 0:
            resultText = self.parseResultTextFile(textPaths[0])
            resultText = re.sub(r"(\n)+$","",resultText)
            resultText = re.sub(r"^(\n)+","",resultText)
        else:
            resultText = currentResult

        self.resultLabel.setText(resultText)
        self.pictureImage = QImage(resultImagePath)
        self.pictureImage = self.pictureImage.scaled(200,200,Qt.IgnoreAspectRatio,Qt.FastTransformation)
        self.pictureLabel.setAlignment( Qt.AlignRight | Qt.AlignVCenter );
        self.pictureLabel.setPixmap(QPixmap.fromImage(self.pictureImage))
        if(len(self.recentList) == 0 or self.recentList[-1] != resultText):
            self.recentList.append(resultText)
            self.recentListWidget.addItem(QListWidgetItem(resultText))
        self.progressBar.setValue(100)
        self.progress = 100.0
        self.progressChangedSignal.emit(self.progress)
        self.progressTimer.stop()
        if(self.continuousMatching and not self.threadInterrupter['interrupted']):
            self.recordAndMatch()
        else:
            self.recordButton.setText(u'Nagrywaj')
            self.recordButton.clicked.disconnect()
            self.recordButton.clicked.connect(self.recordAndMatch)
        self.recordingFinishedSignal.emit(resultText,resultImagePath,resultAudioPath,resultVideoPath)

    def parseResultTextFile(self, textPath):
        with open(textPath) as file:
            result = file.read()
        return result

    def resultTextFormatter(self, result):
        matchedStringFormat = '{artist} - {title}'
        formatedResult = ""
        artist = result['metadata'].get("artist","")
        title = result['metadata'].get("title","")
        msg = result['msg']
        filename = result['filename']
        if artist and title:
            formatedResult = matchedStringFormat.format(**{'artist':artist,'title':title})
        elif filename:
            formatedResult = filename
        elif msg:
            formatedResult = msg
        else:
            formatedResult = u'Coś poszło nie tak...'
        return formatedResult

    progressChangedSignal = pyqtSignal(float)
    def timerEvent(self, e):
        if self.progress >= 100:
            self.progressTimer.stop()
            return
        self.progress = self.progress + 10.0 * 1.0/10.0
        self.progressBar.setValue(self.progress)
        self.progressChangedSignal.emit(self.progress)

    def toggleContinuous(self):
        self.continuousMatching = self.continuousCheckBox.isChecked()
        self.continuousCheckBox.setChecked(self.continuousMatching)

if __name__ == '__main__':
    main(sys.argv)
