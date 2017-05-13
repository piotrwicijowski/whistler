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

class MatcherSettingsDialog(QDialog):

    def __init__(self,parent,continuousMatcher=None):
        super(QDialog,self).__init__(parent)
        self.continuousMatcher = continuousMatcher
        self.initUI()

    def initUI(self):
        if not self.continuousMatcher:
            return

        self.matchWinLabel = QLabel()
        self.matchWinLabel.setText(u'Maksymalne przesunięcie ramek:')
        self.matchWinLineEdit = QLineEdit()
        self.matchWinLineEdit.setText(str(self.continuousMatcher.args['--match-win']))

        self.minCountLabel = QLabel()
        self.minCountLabel.setText(u'Minimalna liczba trafień:')
        self.minCountLineEdit = QLineEdit()
        self.minCountLineEdit.setText(str(self.continuousMatcher.args['--min-count']))

        self.exactCountLabel = QLabel()
        self.exactCountLabel.setText(u'Dokładne liczenie trafień:')
        self.exactCountCheckBox = QCheckBox()
        self.exactCountCheckBox.setChecked(bool(self.continuousMatcher.args['--exact-count']))

        self.dialogButtons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

        self.settingsFormLayout = QFormLayout()
        self.settingsFormLayout.addRow(self.matchWinLabel   , self.matchWinLineEdit)
        self.settingsFormLayout.addRow(self.minCountLabel   , self.minCountLineEdit)
        self.settingsFormLayout.addRow(self.exactCountLabel , self.exactCountCheckBox)

        self.settingsLayout = QVBoxLayout()
        self.settingsLayout.addLayout(self.settingsFormLayout)
        self.settingsLayout.addWidget(self.dialogButtons)
        self.setLayout(self.settingsLayout)

    def run(self):
        if self.exec_():
            self.continuousMatcher.args['--match-win'] = int(self.matchWinLineEdit.text())
            self.continuousMatcher.args['--min-count'] = int(self.minCountLineEdit.text())
            self.continuousMatcher.args['--exact-count'] = self.exactCountCheckBox.isChecked()
            self.continuousMatcher.saveArgsSettings()
