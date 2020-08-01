
import pygame
import pygame.midi
from pygame.locals import *
import math

import random

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal, QTimer, QPoint, QRect, QSize)
import time
import sys

pygame.init()

pygame.fastevent.init()
event_get = pygame.fastevent.get
event_post = pygame.fastevent.post

pygame.midi.init()
input_id = pygame.midi.get_default_input_id()
i = pygame.midi.Input( input_id )


keycode = 0

allgclefkeys = [53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]
notename = ["F", "G", "A", "B", "C", "D", "E", "F", "G", "A", "B", "C", "D", "E", "F", "G", "A", "B", "C"]

randomkeyindex = 3

currNoteName = ''

def generateNewRandomKey():
    global randomkey
    global currNoteName
    global keycode
    global randomkeyindex
    randomkeyindex = random.randint(3, len(allgclefkeys) - 1 - 3)
    # randomkeyindex = 3

    randomkey = allgclefkeys[randomkeyindex]
    print(randomkey, notename[randomkeyindex])
    currNoteName = notename[randomkeyindex]



generateNewRandomKey()


class ClefWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)


        self.width = 500
        self.height = 200

        self.setMinimumSize(self.width, self.height)

        self.gClef = QtGui.QIcon("G-clef.svg")
        self.gClefPixmap = self.gClef.pixmap(QSize(94, 160))

    def drawNoteAt(self, painter, x, staffy):
        y = (14 - staffy) * 10 + 50
        # painter.rotate(-10)
        # painter.drawEllipse(x, staffy*20+50 + (x/2) * math.sin(19 * math.pi / 180.0), 21, 16)
        painter.drawEllipse(x, y, 20, 16)

        if (staffy < 6. or staffy > 14.) and staffy % 2 == 0:
            painter.drawLine(x - 10, y + 10, x + 30, y + 10)

        if staffy < 4.:
            painter.drawLine(x - 10, y + 10 - 10, x + 30, y + 10 - 10)

        if staffy > 16.:
            painter.drawLine(x - 10, y + 10 + 20, x + 30, y + 10 + 20)

        painter.drawText(QPoint(self.width/2, 20), currNoteName)

        # painter.rotate(10)
        # painter.restore()

    def paintEvent(self, e):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)


        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))

        painter.drawPixmap(QRect(0,22, self.gClefPixmap.width(), self.gClefPixmap.height()), self.gClefPixmap)
        #print("keycode:", keycode)


        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        #draw staff
        for y in range(5):
            painter.drawLine(0, 10+20*y+48, self.width, 10+20*y+48)


        global keycode
        global randomkey
        if keycode == randomkey:
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
            generateNewRandomKey()

        else:
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))


        self.drawNoteAt(painter, self.width/2, randomkeyindex)


class AThread(QThread):

    def run(self):
        count = 0
        while True:

            count += 1
            events = event_get()
            for e in events:
                if e.type in [QUIT]:
                    going = False
                if e.type in [KEYDOWN]:
                    going = False

            if i.poll():
                midi_events = i.read(10)
                # print "full midi_events " + str(midi_events)
                print("my midi note is " + str(midi_events[0][0][1]))
                global keycode
                keycode = midi_events[0][0][1]
                # convert them into pygame events.
                midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

                for m_e in midi_evs:
                    event_post(m_e)




#class Ui_MainWindow(object):
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.gameStarted = False
        self.setupStartUi()
        #self.setupGameUi()

    def setupGameUi(self):
        thread = AThread()
        # thread.finished.connect(app.exit)
        thread.start()

        timer = QTimer(self, timeout=self.repaint, interval=100)
        timer.start()

        self.centralwidget = QtWidgets.QWidget(self)
        self.clefw = ClefWidget()
        self.setCentralWidget(self.centralwidget)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")


        self.gridLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.gridLayout.addWidget(self.clefw, 1, 0, 1, 1)

        self.top = 100
        self.left = 100
        self.width = 800
        self.height = 600

        #self.title = "MidiQuiz"
        #self.setObjectName(self.title)

        #self.gClef = QtGui.QIcon("G-clef.svg")
        #self.gClefPixmap = self.gClef.pixmap(QSize(94, 160))

        #self.setWindowIcon(QtGui.QIcon("G-clef.svg"))
        #self.setWindowTitle(self.title)

        #self.gameStarted = True
        self.show()


    def setupStartUi(self):

        self.title = "MidiQuiz"
        self.setObjectName("MainWindow")

        self.gClef = QtGui.QIcon("G-clef.svg")
        self.gClefPixmap = self.gClef.pixmap(QSize(94, 160))

        self.setWindowIcon(QtGui.QIcon("G-clef.svg"))
        self.setWindowTitle(self.title)

        self.setWindowModality(QtCore.Qt.NonModal)
        self.resize(800, 600)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setKerning(True)
        self.setFont(font)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.startButton.setObjectName("startButton")
        self.gridLayout.addWidget(self.startButton, 1, 0, 1, 1)
        self.startButton.clicked.connect(self.setupGameUi)

        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.timeOrNumberOfNotesGridLayout = QtWidgets.QGridLayout()
        self.timeOrNumberOfNotesGridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.timeOrNumberOfNotesGridLayout.setObjectName("timeOrNumberOfNotesGridLayout")
        self.timeOrNumberOfNotesLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeOrNumberOfNotesLabel.sizePolicy().hasHeightForWidth())
        self.timeOrNumberOfNotesLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.timeOrNumberOfNotesLabel.setFont(font)
        self.timeOrNumberOfNotesLabel.setObjectName("timeOrNumberOfNotesLabel")
        self.timeOrNumberOfNotesGridLayout.addWidget(self.timeOrNumberOfNotesLabel, 0, 0, 1, 1)
        self.timeGridLayout = QtWidgets.QGridLayout()
        self.timeGridLayout.setObjectName("timeGridLayout")
        self.minLabel = QtWidgets.QLabel(self.centralwidget)
        self.minLabel.setObjectName("minLabel")
        self.timeGridLayout.addWidget(self.minLabel, 1, 1, 1, 1)
        self.minutesSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.minutesSpinBox.setObjectName("minutesSpinBox")
        self.timeGridLayout.addWidget(self.minutesSpinBox, 1, 0, 1, 1)
        self.unlimitedTimeCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.unlimitedTimeCheckBox.setObjectName("unlimitedTimeCheckBox")
        self.timeGridLayout.addWidget(self.unlimitedTimeCheckBox, 1, 2, 1, 1)
        self.timeRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.timeRadioButton.setObjectName("timeRadioButton")
        self.timeGridLayout.addWidget(self.timeRadioButton, 0, 0, 1, 3)
        self.timeOrNumberOfNotesGridLayout.addLayout(self.timeGridLayout, 0, 1, 1, 1)
        self.numberOfNotesGridLayout = QtWidgets.QGridLayout()
        self.numberOfNotesGridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.numberOfNotesGridLayout.setObjectName("numberOfNotesGridLayout")
        self.notesLabel = QtWidgets.QLabel(self.centralwidget)
        self.notesLabel.setObjectName("notesLabel")
        self.numberOfNotesGridLayout.addWidget(self.notesLabel, 1, 1, 1, 1)
        self.numberOfNotesSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.numberOfNotesSpinBox.setObjectName("numberOfNotesSpinBox")
        self.numberOfNotesGridLayout.addWidget(self.numberOfNotesSpinBox, 1, 0, 1, 1)
        self.unlimitedNotesCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.unlimitedNotesCheckBox.setObjectName("unlimitedNotesCheckBox")
        self.numberOfNotesGridLayout.addWidget(self.unlimitedNotesCheckBox, 1, 2, 1, 1)
        self.numberOfNotesRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.numberOfNotesRadioButton.setObjectName("numberOfNotesRadioButton")
        self.numberOfNotesGridLayout.addWidget(self.numberOfNotesRadioButton, 0, 0, 1, 3)
        self.timeOrNumberOfNotesGridLayout.addLayout(self.numberOfNotesGridLayout, 0, 2, 1, 1)
        self.mainGridLayout.addLayout(self.timeOrNumberOfNotesGridLayout, 3, 0, 1, 1)
        self.noteRangesGridLayout = QtWidgets.QGridLayout()
        self.noteRangesGridLayout.setObjectName("noteRangesGridLayout")
        self.noteRangesLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.noteRangesLabel.sizePolicy().hasHeightForWidth())
        self.noteRangesLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.noteRangesLabel.setFont(font)
        self.noteRangesLabel.setObjectName("noteRangesLabel")
        self.noteRangesGridLayout.addWidget(self.noteRangesLabel, 0, 0, 1, 1)
        self.bassGridLayout = QtWidgets.QGridLayout()
        self.bassGridLayout.setObjectName("bassGridLayout")
        self.highestNoteBassLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.highestNoteBassLabel.sizePolicy().hasHeightForWidth())
        self.highestNoteBassLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.highestNoteBassLabel.setFont(font)
        self.highestNoteBassLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.highestNoteBassLabel.setObjectName("highestNoteBassLabel")
        self.bassGridLayout.addWidget(self.highestNoteBassLabel, 1, 1, 1, 1)
        self.bassLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bassLabel.sizePolicy().hasHeightForWidth())
        self.bassLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.bassLabel.setFont(font)
        self.bassLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.bassLabel.setObjectName("bassLabel")
        self.bassGridLayout.addWidget(self.bassLabel, 0, 0, 1, 2)
        self.lowestNoteBassLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lowestNoteBassLabel.sizePolicy().hasHeightForWidth())
        self.lowestNoteBassLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lowestNoteBassLabel.setFont(font)
        self.lowestNoteBassLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.lowestNoteBassLabel.setObjectName("lowestNoteBassLabel")
        self.bassGridLayout.addWidget(self.lowestNoteBassLabel, 1, 0, 1, 1)
        self.lowestNoteBassComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.lowestNoteBassComboBox.setObjectName("lowestNoteBassComboBox")
        self.bassGridLayout.addWidget(self.lowestNoteBassComboBox, 2, 0, 1, 1)
        self.highestNoteBassComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.highestNoteBassComboBox.setObjectName("highestNoteBassComboBox")
        self.bassGridLayout.addWidget(self.highestNoteBassComboBox, 2, 1, 1, 1)
        self.noteRangesGridLayout.addLayout(self.bassGridLayout, 0, 1, 1, 1)
        self.trebleGridLayout = QtWidgets.QGridLayout()
        self.trebleGridLayout.setObjectName("trebleGridLayout")
        self.trebleLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.trebleLabel.sizePolicy().hasHeightForWidth())
        self.trebleLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.trebleLabel.setFont(font)
        self.trebleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.trebleLabel.setObjectName("trebleLabel")
        self.trebleGridLayout.addWidget(self.trebleLabel, 0, 0, 1, 2)
        self.highestNoteTrebleLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.highestNoteTrebleLabel.sizePolicy().hasHeightForWidth())
        self.highestNoteTrebleLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.highestNoteTrebleLabel.setFont(font)
        self.highestNoteTrebleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.highestNoteTrebleLabel.setObjectName("highestNoteTrebleLabel")
        self.trebleGridLayout.addWidget(self.highestNoteTrebleLabel, 1, 1, 1, 1)
        self.lowestNoteTrebleLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lowestNoteTrebleLabel.sizePolicy().hasHeightForWidth())
        self.lowestNoteTrebleLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lowestNoteTrebleLabel.setFont(font)
        self.lowestNoteTrebleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.lowestNoteTrebleLabel.setObjectName("lowestNoteTrebleLabel")
        self.trebleGridLayout.addWidget(self.lowestNoteTrebleLabel, 1, 0, 1, 1)
        self.lowestNoteTrebleComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.lowestNoteTrebleComboBox.setObjectName("lowestNoteTrebleComboBox")
        self.trebleGridLayout.addWidget(self.lowestNoteTrebleComboBox, 2, 0, 1, 1)
        self.highestNoteTrebleComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.highestNoteTrebleComboBox.setObjectName("highestNoteTrebleComboBox")
        self.trebleGridLayout.addWidget(self.highestNoteTrebleComboBox, 2, 1, 1, 1)
        self.noteRangesGridLayout.addLayout(self.trebleGridLayout, 0, 2, 1, 1)
        self.mainGridLayout.addLayout(self.noteRangesGridLayout, 6, 0, 1, 1)
        self.notesToDisplayGridLayout = QtWidgets.QGridLayout()
        self.notesToDisplayGridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.notesToDisplayGridLayout.setObjectName("notesToDisplayGridLayout")
        self.trebleCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.trebleCheckBox.setFont(font)
        self.trebleCheckBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.trebleCheckBox.setObjectName("trebleCheckBox")
        self.notesToDisplayGridLayout.addWidget(self.trebleCheckBox, 0, 1, 1, 1)
        self.notesToDisplayLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.notesToDisplayLabel.sizePolicy().hasHeightForWidth())
        self.notesToDisplayLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.notesToDisplayLabel.setFont(font)
        self.notesToDisplayLabel.setObjectName("notesToDisplayLabel")
        self.notesToDisplayGridLayout.addWidget(self.notesToDisplayLabel, 0, 0, 1, 1)
        self.baseCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.baseCheckBox.setFont(font)
        self.baseCheckBox.setObjectName("baseCheckBox")
        self.notesToDisplayGridLayout.addWidget(self.baseCheckBox, 0, 2, 1, 1)
        self.mainGridLayout.addLayout(self.notesToDisplayGridLayout, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.mainGridLayout.addWidget(self.line, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.mainGridLayout.addWidget(self.line_2, 5, 0, 1, 1)
        self.gridLayout.addLayout(self.mainGridLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 782, 18))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.timeOrNumberOfNotesLabel.setText(_translate("MainWindow", "Time or number of notes?"))
        self.minLabel.setText(_translate("MainWindow", "min"))
        self.unlimitedTimeCheckBox.setText(_translate("MainWindow", "Unlimited"))
        self.timeRadioButton.setText(_translate("MainWindow", "Time"))
        self.notesLabel.setText(_translate("MainWindow", "notes"))
        self.unlimitedNotesCheckBox.setText(_translate("MainWindow", "Unlimited"))
        self.numberOfNotesRadioButton.setText(_translate("MainWindow", "Number of notes"))
        self.noteRangesLabel.setText(_translate("MainWindow", "Note ranges"))
        self.highestNoteBassLabel.setText(_translate("MainWindow", "Highest note:"))
        self.bassLabel.setText(_translate("MainWindow", "Bass"))
        self.lowestNoteBassLabel.setText(_translate("MainWindow", "Lowest note:"))
        self.trebleLabel.setText(_translate("MainWindow", "Treble"))
        self.highestNoteTrebleLabel.setText(_translate("MainWindow", "Highest note:"))
        self.lowestNoteTrebleLabel.setText(_translate("MainWindow", "Lowest note:"))
        self.trebleCheckBox.setText(_translate("MainWindow", "Treble"))
        self.notesToDisplayLabel.setText(_translate("MainWindow", "Notes to display"))
        self.baseCheckBox.setText(_translate("MainWindow", "Bass"))





App = QApplication(sys.argv)
window = MainWindow()
sys.exit(App.exec())
