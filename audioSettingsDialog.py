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
import microphone_match

class AudioSettingDialog(QDialog):

    def __init__(self,parent,continuousMatcher=None):
        super(QDialog,self).__init__(parent)
        self.continuousMatcher = continuousMatcher
        self.initUI()

    def initUI(self):
        if not self.continuousMatcher:
            return

        self.audioBinLabel = QLabel()
        self.audioBinLabel.setText(u'Ścieżka do ffmpeg:')
        self.audioBinLineEdit = QLineEdit()
        self.audioBinLineEdit.setText(self.continuousMatcher.FFMpegBin)

        self.audioDeviceLabel = QLabel()
        self.audioDeviceLabel.setText(u'Urządzenie audio:')
        self.audioDeviceLineEdit = QLineEdit()
        self.audioDeviceLineEdit.setText(self.continuousMatcher.FFMpegDevice)

        self.audioInputLabel = QLabel()
        self.audioInputLabel.setText(u'Wejście audio:')
        self.audioInputLineEdit = QLineEdit()
        self.audioInputLineEdit.setText(self.continuousMatcher.FFMpegInput)

        self.audioInputChannelsLabel = QLabel()
        self.audioInputChannelsLabel.setText(u'Ilość kanałów wejścia:')
        self.audioInputChannelsLineEdit = QLineEdit()
        self.audioInputChannelsLineEdit.setText(str(self.continuousMatcher.FFMpegInputChannels))

        self.dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

        self.settingsFormLayout = QFormLayout()
        self.settingsFormLayout.addRow(self.audioBinLabel,           self.audioBinLineEdit)
        self.settingsFormLayout.addRow(self.audioDeviceLabel,        self.audioDeviceLineEdit)
        self.settingsFormLayout.addRow(self.audioInputLabel,         self.audioInputLineEdit)
        self.settingsFormLayout.addRow(self.audioInputChannelsLabel, self.audioInputChannelsLineEdit)

        self.settingsLayout = QVBoxLayout()
        self.settingsLayout.addLayout(self.settingsFormLayout)
        self.settingsLayout.addWidget(self.dialogButtons)
        self.setLayout(self.settingsLayout)

    def run(self):
        if self.exec_():
            self.continuousMatcher.FFMpegBin           = unicode(self.audioBinLineEdit.text())
            self.continuousMatcher.FFMpegDevice        = unicode(self.audioDeviceLineEdit.text())
            self.continuousMatcher.FFMpegInput         = unicode(self.audioInputLineEdit.text())
            self.continuousMatcher.FFMpegInputChannels = int(self.audioInputChannelsLineEdit.text())
            self.continuousMatcher.saveFFMpegSettings()
