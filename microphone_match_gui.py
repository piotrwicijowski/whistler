#!/usr/bin/python2
# -*- coding: utf-8 -*-

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import sys
import os
import datetime
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
from PyQt5.QtCore import (QCoreApplication, QThread, QBasicTimer, QUrl, pyqtProperty, pyqtSlot, pyqtSignal, Qt)
from PyQt5.QtQml import (qmlRegisterType, QQmlComponent, QQmlEngine)
from PyQt5.QtQuick import (QQuickView)
from PyQt5.QtQuickWidgets import (QQuickWidget)
import locale
os_encoding = locale.getpreferredencoding()
import microphone_match
import scannerSettingsDialog
import matcherSettingsDialog
import audioSettingsDialog

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

        self.centralWidget = QWidget(self)
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
        if self.fullscreenWindow == None:
            self.fullscreenWindow = QDialog(self)
            widget = QQuickWidget(self.fullscreenWindow)
            layout = QVBoxLayout(self.fullscreenWindow)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(widget)
            self.fullscreenWindow.setLayout(layout)
            widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
            # view = QQuickView()
            widget.setSource(QUrl('fullscreen.qml'))
            # engine = widget.engine()
            mainRootObject = widget.rootObject()
            mainRootObject.startRecording.connect(self.recordAndMatch)
            mainRootObject.closeWindow.connect(self.closeFullscreenWindow)
            self.recordingStartedSignal.connect(mainRootObject.stateRecording)
            self.recordingFinishedSignal.connect(mainRootObject.stateReady)
            self.fullscreenWindow.showFullScreen()
        else:
            self.fullscreenWindow.show()

    def closeFullscreenWindow(self):
        if self.fullscreenWindow != None:
            self.fullscreenWindow.close()
            del self.fullscreenWindow
            self.fullscreenWindow = None

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

    recordingStartedSignal = pyqtSignal()
    def recordAndMatch(self):
        self.threadInterrupter['interrupted'] = False
        self.recordButton.setText(u'Nagrywanie')
        self.progress = 0.0
        self.progressBar.setValue(0)
        self.progressTimer.start(100,self)
        self.matcherThread.start()
        self.recordButton.clicked.disconnect()
        self.recordButton.clicked.connect(self.interruptRecording)
        self.recordingStartedSignal.emit()

    recordingFinishedSignal = pyqtSignal(str)
    def recordingFinished(self):
        currentResult = self.resultTextFormatter(self.matcherThread.result)
        imagePath = os.path.splitext(self.matcherThread.result["filename"])[0] + '.jpg'
        imagePath = os.path.join(self.continuousMatcher.applicationPath, imagePath)
        imagePath = os.path.normpath(imagePath)
        self.resultLabel.setText(currentResult)
        self.pictureImage = QImage(imagePath)
        self.pictureImage = self.pictureImage.scaled(200,200,Qt.IgnoreAspectRatio,Qt.FastTransformation)
        self.pictureLabel.setAlignment( Qt.AlignRight | Qt.AlignVCenter );
        self.pictureLabel.setPixmap(QPixmap.fromImage(self.pictureImage))
        if(len(self.recentList) == 0 or self.recentList[-1] != currentResult):
            self.recentList.append(currentResult)
            self.recentListWidget.addItem(QListWidgetItem(currentResult))
        self.progressBar.setValue(100)
        self.progress = 100.0
        self.progressTimer.stop()
        if(self.continuousMatching and not self.threadInterrupter['interrupted']):
            self.recordAndMatch()
        else:
            self.recordButton.setText(u'Nagrywaj')
            self.recordButton.clicked.disconnect()
            self.recordButton.clicked.connect(self.recordAndMatch)
        self.recordingFinishedSignal.emit(currentResult)

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

    def timerEvent(self, e):
        if self.progress >= 100:
            self.progressTimer.stop()
            return
        self.progress = self.progress + 10.0 * 1.0/10.0
        self.progressBar.setValue(self.progress)

    def toggleContinuous(self):
        self.continuousMatching = self.continuousCheckBox.isChecked()
        self.continuousCheckBox.setChecked(self.continuousMatching)

if __name__ == '__main__':
    main(sys.argv)
