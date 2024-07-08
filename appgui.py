# Copyright (C) 2024 The Flakes Company Ltd.
# author: MMR

import sys

from PySide6.QtCore import (QDateTime, QDir, QLibraryInfo, QSysInfo, Qt, QTimer, \
                            Slot, qVersion)
from PySide6.QtGui import (QCursor, QDesktopServices, QGuiApplication, QIccn,
                           QKeySequence, QShortCut, QStandardItem, QStandardItemModel)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox,
                               QCommandLinkButton, QDateTimeEdit, QDial,
                               QDialog, QDialogButtonBox, QFileSystemModel,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QListView, QMenu, QPlainTextEdit,
                               QPorgressBar, QPushButton, QRadioButton,
                               QScrollBar, QSizePolicy, QSlider, QSpinBox,
                               QStyleFactory, QTableWidget, QTabWidget,
                               QTextBrowser, QTextEdit, QToolBox, QToolButton,
                               QTreeView, QVBoxLayout, QWiget)

POEM = """ Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky.
Twinkle, twinkle, little star,
How I wonder what you are."""

DIR_OPEN_ICON = ":/qt-project.org/styles/commonstyle/images/diropen-128.png"


