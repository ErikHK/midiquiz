
import pygame
import pygame.midi
from pygame.locals import *
import math
import datetime

import random

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont
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
midiInput = pygame.midi.Input( input_id )


keycode = 0

allgclefkeys = [53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]
notename = ["F", "G", "A", "B", "C", "D", "E", "F", "G", "A", "B", "C", "D", "E", "F", "G", "A", "B", "C"]

fullnotenamesf = ["A1", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4"]
fullnotenamesg = ["F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]


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


        font = QFont()
        font.setPointSize(14)
        painter.setFont(font)
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
            #generateNewRandomKey()

        else:
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))


        self.drawNoteAt(painter, self.width/2, randomkeyindex)


class MidiThread(QThread):

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

            if midiInput.poll():
                midi_events = midiInput.read(10)
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
        self.time = 0.0
        self.numberOfNotes = 0
        self.timeForLastNote = -1
        self.accuracy = -1

        self.score = 0


        self.setupStartUi()
        #self.setupGameUi()

        #repaint UI
        timer = QTimer(self, timeout=self.repaint, interval=10)
        timer.start()

        self.midiPollingTimer = QTimer(self, timeout=self.midiPolling, interval=100)



    def midiPolling(self):
        #print("midipolling")
        if midiInput.poll():
            midi_events = midiInput.read(10)
            # print "full midi_events " + str(midi_events)
            print("my midi note is " + str(midi_events[0][0][1]))
            global keycode
            keycode = midi_events[0][0][1]
            down = midi_events[0][0][2]

            if keycode >= 36 and keycode <= 96:
                if down:
                    self.numberOfNotes += 1
                    if keycode == randomkey:
                        self.midiPollingTimer.stop()
                        self.repaint()
                        self.score += 1
                        time.sleep(.5)

                        generateNewRandomKey()
                        self.midiPollingTimer.start()
                    else:
                        self.midiPollingTimer.stop()
                        self.repaint()
                        time.sleep(.5)
                        self.midiPollingTimer.start()


    def increaseTime(self):
        self.time += .1

        self.totalTimeLabel.setText(str(datetime.timedelta(seconds=int(self.time))))
        if self.accuracy != -1:
            self.accuracyLabel.setText(str(self.accuracy))
        if self.timeForLastNote != -1:
            self.timeForLastNoteLabel.setText(str(self.timeForLastNote))
        self.numberOfNotesLabel.setText(str(self.numberOfNotes))

        self.scoreLabel.setText(str(self.score))


    def startGame(self):
        self.setupGameUi()

        timer = QTimer(self, timeout=self.increaseTime, interval=100)
        timer.start()


        self.midiPollingTimer.start()

    def setupGameUi(self):
        #Midi polling thread
        #thread = MidiThread()
        #thread.start()

        #timer = QTimer(self, timeout=self.repaint, interval=100)
        #timer.start()

        self.centralwidget = QtWidgets.QWidget(self)
        #self.clefw = ClefWidget()
        #self.setCentralWidget(self.centralwidget)

        #self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        #self.gridLayout.setObjectName("gridLayout")


        #self.gridLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        #self.gridLayout.addWidget(self.clefw, 1, 0, 1, 1)

        #self.timeLabel.setText((str(self.time)))
        #self.gridLayout.addWidget(self.timeLabel, 2, 0, 1, 2)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        #self.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pausePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pausePushButton.setObjectName("pausePushButton")
        self.gridLayout_2.addWidget(self.pausePushButton, 1, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        #self.newgridl = QtWidgets.QGridLayout(self)

        self.clefWidget = ClefWidget()#QtWidgets.QOpenGLWidget(self.centralwidget)
        self.clefWidget.setObjectName("clefWidget")

        self.clefWidgetGridLayout = QtWidgets.QGridLayout()
        self.clefWidgetGridLayout.setObjectName("clefWidgetGridLayout")
        #self.verticalLayout.setAlignment(QtCore.Qt.AlignRight)

        #self.verticalLayout.addWidget(self.clefWidget)

        #self.newgridl.addWidget(self.verticalLayout,1,1,1,1)
        #self.newgridl.addWidget(self.clefWidget)
        self.clefWidgetGridLayout.addWidget(self.clefWidget, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.clefWidgetGridLayout)


        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.numberOfNotesGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.numberOfNotesGroupBox.setFont(font)
        self.numberOfNotesGroupBox.setObjectName("numberOfNotesGroupBox")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.numberOfNotesGroupBox)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.numberOfNotesGridLayout = QtWidgets.QGridLayout()
        self.numberOfNotesGridLayout.setObjectName("numberOfNotesGridLayout")
        self.numberOfNotesLabel = QtWidgets.QLabel(self.numberOfNotesGroupBox)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.numberOfNotesLabel.setFont(font)
        self.numberOfNotesLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.numberOfNotesLabel.setObjectName("numberOfNotesLabel")
        self.numberOfNotesGridLayout.addWidget(self.numberOfNotesLabel, 0, 0, 1, 1)
        self.gridLayout_7.addLayout(self.numberOfNotesGridLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.numberOfNotesGroupBox, 1, 0, 1, 1)
        self.scoreGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.scoreGroupBox.setFont(font)
        self.scoreGroupBox.setObjectName("scoreGroupBox")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.scoreGroupBox)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.scoreGridLayout = QtWidgets.QGridLayout()
        self.scoreGridLayout.setObjectName("scoreGridLayout")
        self.scoreDescLabel = QtWidgets.QLabel(self.scoreGroupBox)
        self.scoreDescLabel.setObjectName("scoreDescLabel")
        self.scoreGridLayout.addWidget(self.scoreDescLabel, 0, 0, 1, 1)
        self.accuracyDescLabel = QtWidgets.QLabel(self.scoreGroupBox)
        self.accuracyDescLabel.setObjectName("accuracyDescLabel")
        self.scoreGridLayout.addWidget(self.accuracyDescLabel, 1, 0, 1, 1)
        self.scoreLabel = QtWidgets.QLabel(self.scoreGroupBox)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.scoreLabel.setFont(font)
        self.scoreLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.scoreLabel.setObjectName("scoreLabel")
        self.scoreGridLayout.addWidget(self.scoreLabel, 0, 1, 1, 1)
        self.accuracyLabel = QtWidgets.QLabel(self.scoreGroupBox)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.accuracyLabel.setFont(font)
        self.accuracyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.accuracyLabel.setObjectName("accuracyLabel")
        self.scoreGridLayout.addWidget(self.accuracyLabel, 1, 1, 1, 1)
        self.gridLayout_9.addLayout(self.scoreGridLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.scoreGroupBox, 0, 2, 2, 1)
        self.timeGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.timeGroupBox.setFont(font)
        self.timeGroupBox.setObjectName("timeGroupBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.timeGroupBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.timeGridLayout = QtWidgets.QGridLayout()
        self.timeGridLayout.setObjectName("timeGridLayout")
        self.timeForLastNoteDescLabel = QtWidgets.QLabel(self.timeGroupBox)
        self.timeForLastNoteDescLabel.setObjectName("timeForLastNoteDescLabel")
        self.timeGridLayout.addWidget(self.timeForLastNoteDescLabel, 1, 0, 1, 1)
        self.totalTimeDescLabel = QtWidgets.QLabel(self.timeGroupBox)
        self.totalTimeDescLabel.setObjectName("totalTimeDescLabel")
        self.timeGridLayout.addWidget(self.totalTimeDescLabel, 0, 0, 1, 1)
        self.averageTimePerNoteDescLabel = QtWidgets.QLabel(self.timeGroupBox)
        self.averageTimePerNoteDescLabel.setObjectName("averageTimePerNoteDescLabel")
        self.timeGridLayout.addWidget(self.averageTimePerNoteDescLabel, 2, 0, 1, 1)
        self.totalTimeLabel = QtWidgets.QLabel(self.timeGroupBox)
        self.totalTimeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.totalTimeLabel.setObjectName("totalTimeLabel")
        self.timeGridLayout.addWidget(self.totalTimeLabel, 0, 1, 1, 1)
        self.timeForLastNoteLabel = QtWidgets.QLabel(self.timeGroupBox)
        self.timeForLastNoteLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.timeForLastNoteLabel.setObjectName("timeForLastNoteLabel")
        self.timeGridLayout.addWidget(self.timeForLastNoteLabel, 1, 1, 1, 1)
        self.averageTimePerNoteLabel = QtWidgets.QLabel(self.timeGroupBox)
        self.averageTimePerNoteLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.averageTimePerNoteLabel.setObjectName("averageTimePerNoteLabel")
        self.timeGridLayout.addWidget(self.averageTimePerNoteLabel, 2, 1, 1, 1)
        self.gridLayout_5.addLayout(self.timeGridLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.timeGroupBox, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.quitPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitPushButton.setObjectName("quitPushButton")
        self.gridLayout_2.addWidget(self.quitPushButton, 2, 1, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 805, 18))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.retranslateGameUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()


    def retranslateGameUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pausePushButton.setText(_translate("MainWindow", "Pause"))
        self.numberOfNotesGroupBox.setTitle(_translate("MainWindow", "Number of notes"))
        #self.numberOfNotesLabel.setText(_translate("MainWindow", "TextLabel"))
        self.scoreGroupBox.setTitle(_translate("MainWindow", "Score"))
        self.scoreDescLabel.setText(_translate("MainWindow", "Score:"))
        self.accuracyDescLabel.setText(_translate("MainWindow", "Accuracy (%):"))
        self.scoreLabel.setText(_translate("MainWindow", "TextLabel"))
        #self.accuracyLabel.setText(_translate("MainWindow", "TextLabel"))
        self.timeGroupBox.setTitle(_translate("MainWindow", "Time"))
        self.timeForLastNoteDescLabel.setText(_translate("MainWindow", "Time for last note:"))
        self.totalTimeDescLabel.setText(_translate("MainWindow", "Total time:"))
        self.averageTimePerNoteDescLabel.setText(_translate("MainWindow", "Average time per note:"))
        #self.totalTimeLabel.setText(_translate("MainWindow", "TextLabel"))
        #self.timeForLastNoteLabel.setText(_translate("MainWindow", "TextLabel"))
        #self.averageTimePerNoteLabel.setText(_translate("MainWindow", "TextLabel"))
        self.quitPushButton.setText(_translate("MainWindow", "Quit"))





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
        self.startButton.clicked.connect(self.startGame)

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
        self.minutesSpinBox.setValue(1)
        self.timeGridLayout.addWidget(self.minutesSpinBox, 1, 0, 1, 1)
        self.unlimitedTimeCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.unlimitedTimeCheckBox.setObjectName("unlimitedTimeCheckBox")
        self.timeGridLayout.addWidget(self.unlimitedTimeCheckBox, 1, 2, 1, 1)
        self.timeRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.timeRadioButton.setObjectName("timeRadioButton")
        self.timeRadioButton.setChecked(True)
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
        self.numberOfNotesSpinBox.setValue(50)
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
        self.lowestNoteBassComboBox.addItems(fullnotenamesf)
        self.bassGridLayout.addWidget(self.lowestNoteBassComboBox, 2, 0, 1, 1)

        self.highestNoteBassComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.highestNoteBassComboBox.setObjectName("highestNoteBassComboBox")
        self.highestNoteBassComboBox.addItems(fullnotenamesf)
        self.highestNoteBassComboBox.setCurrentIndex(len(fullnotenamesf)-1)
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
        self.lowestNoteTrebleComboBox.addItems(fullnotenamesg)
        self.lowestNoteTrebleComboBox.setEnabled(True)
        self.trebleGridLayout.addWidget(self.lowestNoteTrebleComboBox, 2, 0, 1, 1)

        self.highestNoteTrebleComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.highestNoteTrebleComboBox.setObjectName("highestNoteTrebleComboBox")
        self.highestNoteTrebleComboBox.addItems(fullnotenamesg)
        self.highestNoteTrebleComboBox.setCurrentIndex(len(fullnotenamesg)-1)
        self.trebleGridLayout.addWidget(self.highestNoteTrebleComboBox, 2, 1, 1, 1)

        self.noteRangesGridLayout.addLayout(self.trebleGridLayout, 0, 2, 1, 1)
        self.mainGridLayout.addLayout(self.noteRangesGridLayout, 6, 0, 1, 1)
        self.notesToDisplayGridLayout = QtWidgets.QGridLayout()
        self.notesToDisplayGridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.notesToDisplayGridLayout.setObjectName("notesToDisplayGridLayout")
        self.trebleCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.trebleCheckBox.setChecked(True)
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

        self.retranslateStartUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def retranslateStartUi(self):
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
