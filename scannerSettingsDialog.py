#!/usr/bin/python2
# -*- coding: utf-8 -*-

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
import locale
os_encoding = locale.getpreferredencoding()
import microphone_match

class ScannerSettingsDialog(QDialog):

    def __init__(self,parent,continuousMatcher=None):
        super(QDialog,self).__init__(parent)
        self.continuousMatcher = continuousMatcher
        self.initUI()

    def initUI(self):
        if not self.continuousMatcher:
            return

        self.densityLabel = QLabel()
        self.densityLabel.setText(u'Gęstość znaczników na sekundę')
        self.densityLineEdit = QLineEdit()
        self.densityLineEdit.setText(str(self.continuousMatcher.args['--density']))

        self.hashbitsLabel = QLabel()
        self.hashbitsLabel.setText(u'Ilość bitów na znacznik')
        self.hashbitsLineEdit = QLineEdit()
        self.hashbitsLineEdit.setText(str(self.continuousMatcher.args['--hashbits']))

        self.bucketsizeLabel = QLabel()
        self.bucketsizeLabel.setText(u'Rozmiar kubła znaczników')
        self.bucketsizeLineEdit = QLineEdit()
        self.bucketsizeLineEdit.setText(str(self.continuousMatcher.args['--bucketsize']))

        self.maxtimeLabel = QLabel()
        self.maxtimeLabel.setText(u'Maksymalny zapisany czas')
        self.maxtimeLineEdit = QLineEdit()
        self.maxtimeLineEdit.setText(str(self.continuousMatcher.args['--maxtime']))

        self.samplerateLabel = QLabel()
        self.samplerateLabel.setText(u'Częstotliwość próbkowania')
        self.samplerateLineEdit = QLineEdit()
        self.samplerateLineEdit.setText(str(self.continuousMatcher.args['--samplerate']))

        self.shiftsLabel = QLabel()
        self.shiftsLabel.setText(u'Ilość przesunięć przy liczeniu odcisków')
        self.shiftsLineEdit = QLineEdit()
        self.shiftsLineEdit.setText(str(self.continuousMatcher.args['--shifts']))

        self.quantileLabel = QLabel()
        self.quantileLabel.setText(u'Kwantyl dla extremów')
        self.quantileLineEdit = QLineEdit()
        self.quantileLineEdit.setText(str(self.continuousMatcher.args['--time-quantile']))

        self.frequencySDLabel = QLabel()
        self.frequencySDLabel.setText(u'Częstotliwość SD')
        self.frequencySDLineEdit = QLineEdit()
        self.frequencySDLineEdit.setText(str(self.continuousMatcher.args['--freq-sd']))

        self.fanoutLabel = QLabel()
        self.fanoutLabel.setText(u'Maksymalna ilość par znaczników na szczyt')
        self.fanoutLineEdit = QLineEdit()
        self.fanoutLineEdit.setText(str(self.continuousMatcher.args['--fanout']))

        self.pksPerFrameLabel = QLabel()
        self.pksPerFrameLabel.setText(u'Ilość szczytów na ramkę')
        self.pksPerFrameLineEdit = QLineEdit()
        self.pksPerFrameLineEdit.setText(str(self.continuousMatcher.args['--pks-per-frame']))

        self.searchDepthLabel = QLabel()
        self.searchDepthLabel.setText(u'Głębokość wyszukiwania')
        self.searchDepthLineEdit = QLineEdit()
        self.searchDepthLineEdit.setText(str(self.continuousMatcher.args['--search-depth']))

        self.dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

        self.settingsFormLayout = QFormLayout()
        self.settingsFormLayout.addRow(self.densityLabel     , self.densityLineEdit)
        self.settingsFormLayout.addRow(self.hashbitsLabel    , self.hashbitsLineEdit)
        self.settingsFormLayout.addRow(self.bucketsizeLabel  , self.bucketsizeLineEdit)
        self.settingsFormLayout.addRow(self.maxtimeLabel     , self.maxtimeLineEdit)
        self.settingsFormLayout.addRow(self.samplerateLabel  , self.samplerateLineEdit)
        self.settingsFormLayout.addRow(self.shiftsLabel      , self.shiftsLineEdit)
        self.settingsFormLayout.addRow(self.quantileLabel    , self.quantileLineEdit)
        self.settingsFormLayout.addRow(self.frequencySDLabel , self.frequencySDLineEdit)
        self.settingsFormLayout.addRow(self.fanoutLabel      , self.fanoutLineEdit)
        self.settingsFormLayout.addRow(self.pksPerFrameLabel , self.pksPerFrameLineEdit)
        self.settingsFormLayout.addRow(self.searchDepthLabel , self.searchDepthLineEdit)

        self.settingsLayout = QVBoxLayout()
        self.settingsLayout.addLayout(self.settingsFormLayout)
        self.settingsLayout.addWidget(self.dialogButtons)
        self.setLayout(self.settingsLayout)
    def run(self):
        if self.exec_():
            self.continuousMatcher.args['--density']       = float ( self.densityLineEdit.text())
            self.continuousMatcher.args['--hashbits']      = int   ( self.hashbitsLineEdit.text())
            self.continuousMatcher.args['--bucketsize']    = int   ( self.bucketsizeLineEdit.text())
            self.continuousMatcher.args['--maxtime']       = int   ( self.maxtimeLineEdit.text())
            self.continuousMatcher.args['--samplerate']    = int   ( self.samplerateLineEdit.text())
            self.continuousMatcher.args['--shifts']        = int   ( self.shiftsLineEdit.text())
            self.continuousMatcher.args['--time-quantile'] = float ( self.quantileLineEdit.text())
            self.continuousMatcher.args['--freq-sd']       = float ( self.frequencySDLineEdit.text())
            self.continuousMatcher.args['--fanout']        = int   ( self.fanoutLineEdit.text())
            self.continuousMatcher.args['--pks-per-frame'] = int   ( self.pksPerFrameLineEdit.text())
            self.continuousMatcher.args['--search-depth']  = int   ( self.searchDepthLineEdit.text())
            self.continuousMatcher.saveArgsSettings()
