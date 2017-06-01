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

class UiSettingDialog(QDialog):

    def __init__(self,parent,continuousMatcher=None):
        super(QDialog,self).__init__(parent)
        self.continuousMatcher = continuousMatcher
        self.initUI()

    def initUI(self):
        if not self.continuousMatcher:
            return

        self.fullscreenLabel = QLabel()
        self.fullscreenLabel.setText(u'Startuj w pełnym ekranie:')
        self.fullscreenCheckBox = QCheckBox()
        self.fullscreenCheckBox.setChecked(self.continuousMatcher.startFullscreen)

        self.playbackLabel = QLabel()
        self.playbackLabel.setText(u'Pozwól na odtwarzanie dopasowania:')
        self.playbackCheckBox = QCheckBox()
        self.playbackCheckBox.setChecked(self.continuousMatcher.enablePlayback)

        self.autoPlaybackLabel = QLabel()
        self.autoPlaybackLabel.setText(u'Automatyczne odtwarzanie:')
        self.autoPlaybackCheckBox = QCheckBox()
        self.autoPlaybackCheckBox.setChecked(self.continuousMatcher.autoPlayback)

        self.dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

        self.settingsFormLayout = QFormLayout()
        self.settingsFormLayout.addRow(self.fullscreenLabel,   self.fullscreenCheckBox)
        self.settingsFormLayout.addRow(self.playbackLabel,     self.playbackCheckBox)
        self.settingsFormLayout.addRow(self.autoPlaybackLabel, self.autoPlaybackCheckBox)

        self.settingsLayout = QVBoxLayout()
        self.settingsLayout.addLayout(self.settingsFormLayout)
        self.settingsLayout.addWidget(self.dialogButtons)
        self.setLayout(self.settingsLayout)

    def run(self):
        if self.exec_():
            self.continuousMatcher.startFullscreen = bool(self.fullscreenCheckBox.isChecked())
            self.continuousMatcher.enablePlayback  = bool(self.playbackCheckBox.isChecked())
            self.continuousMatcher.autoPlayback    = bool(self.autoPlaybackCheckBox.isChecked())
            self.continuousMatcher.saveUiSettings()
