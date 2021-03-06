
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

import statistics

pygame.init()

pygame.midi.init()
input_id = pygame.midi.get_default_input_id()

#guess that MIDI exists
midiInputExists = True
try:
    midiInput = pygame.midi.Input( input_id )
except:
    midiInputExists = False

keycode = 0

allGClefKeyCodes = [53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88]
allFClefKeyCodes = [33, 35, 36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67]

fullNotenamesF = ["A1", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4"]
noteNamesF = ["A", "B", "C", "D", "E", "F", "G", "A", "B", "C", "D", "E", "F", "G"]
fullNotenamesG = ["F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6", "D6", "E6"]
noteNamesG = ["F", "G", "A", "B", "C", "D", "E", "F", "G", "A", "B", "C", "D", "E", "F", "G", "A", "B", "C", "D", "E"]

class Note():
    def __init__(self, fullName, gClef, index):
        self.fullName = fullName
        self.index = index
        self.gClef = gClef
        self.played = False

        if self.gClef:
            self.midiCode = allGClefKeyCodes[fullNotenamesG.index(self.fullName)]
        else:
            self.midiCode = allFClefKeyCodes[fullNotenamesF.index(self.fullName)]
    def setPlayed(self):
        self.played = True

    def isPlayed(self):
        return self.played

    def code(self):
        return self.midiCode

    def __str__(self):
        return self.fullName

    def name(self):
        return self.fullName[0]

class SheetLogic():
    def __init__(self):
        self.notes = []

        self.gClefNotes = []
        self.fClefNotes = []

    def allPlayed(self):
        for n in self.gClefNotes:
            print("notes", n.name(), n.fullName, n.isPlayed())
            if not n.isPlayed():
                return False
        for n in self.fClefNotes:
            if not n.isPlayed():
                return False
        return True

    def setCharNotePlayed(self, noteName):
        for note in self.gClefNotes:
            if note.name() == noteName:
                note.setPlayed()
        for note in self.fClefNotes:
            if note.name() == noteName:
                note.setPlayed()

    def setKeycodeNotePlayed(self, noteCode):
        for note in self.gClefNotes:
            if note.code() == noteCode:
                note.setPlayed()
        for note in self.fClefNotes:
            if note.code() == noteCode:
                note.setPlayed()

    def keyCodeInGNoteList(self, code):
        tmplist = [note.code() for note in self.gClefNotes]
        return code in tmplist

    def noteInGNoteList(self, noteName):
        tmplist = [note.name() for note in self.gClefNotes]
        return noteName in tmplist

    def keyCodeInFNoteList(self, code):
        tmplist = [note.code() for note in self.gClefNotes]
        return code in tmplist

    def noteInFNoteList(self, noteName):
        pass
        tmplist = [note.name() for note in self.fClefNotes]
        return noteName in tmplist


    def generateRandomNotes(self, minBassNote, maxBassNote, minTrebleNote, maxTrebleNote,
                            lowestBassNote, highestBassNote, lowestTrebleNote, highestTrebleNote):


        self.numberOfBassNotes = random.randint(minBassNote, maxBassNote)
        self.numberOfTrebleNotes = random.randint(minTrebleNote, maxTrebleNote)

        self.gClefNotes = []
        self.fClefNotes = []

        for n in range(self.numberOfBassNotes):
            ind = random.randint(lowestBassNote, highestBassNote)
            note = Note(fullNotenamesF[ind], False, n)
            self.fClefNotes.append(note)

        for n in range(self.numberOfTrebleNotes):
            ind = random.randint(lowestTrebleNote, highestTrebleNote)
            note = Note(fullNotenamesG[ind], True, n)
            self.gClefNotes.append(note)

class ClefWidget(QtWidgets.QWidget):

    def __init__(self, clefNotes, gClef = True):
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.width = 500
        self.height = 230
        self.drawGreen = [False for i in range(len(clefNotes))]
        self.drawRed = [False for i in range(len(clefNotes))]

        self.setMinimumSize(self.width, self.height)

        self.clefNotes = clefNotes

        self.gClef = gClef
        if self.gClef:
            self.clef = QtGui.QIcon("G-clef.svg")
            self.clefPixmap = self.clef.pixmap(QSize(94, 160))
            self.offsx = 0
            self.offsy = 22+20
        else:
            self.clef = QtGui.QIcon("F-clef.svg")
            self.clefPixmap = self.clef.pixmap(QSize(61, 104))
            self.offsx = 20
            self.offsy = 57+20

        self.wholeNote = QtGui.QIcon("Whole-note.svg")
        self.wholeNotePixmap = self.wholeNote.pixmap(QSize(32, 17))

        self.wholeNoteGreen = QtGui.QIcon("Whole-note-green.svg")
        self.wholeNoteGreenPixmap = self.wholeNoteGreen.pixmap(QSize(32, 17))

        self.wholeNoteRed = QtGui.QIcon("Whole-note-red.svg")
        self.wholeNoteRedPixmap = self.wholeNoteRed.pixmap(QSize(32, 17))

    def updateNotes(self, clefNotes):
        self.clefNotes = clefNotes

    def drawNotes(self, painter):
        for n,note in enumerate(self.clefNotes):
            x = int(n*60 + self.width/2 - 150)
            if self.gClef:
                ind = allGClefKeyCodes.index(self.clefNotes[n].code())
            else:
                ind = allFClefKeyCodes.index(self.clefNotes[n].code())

            y = int((14-ind) * 10 + 70)

            if note.isPlayed():
                painter.drawPixmap(QRect(x, y, self.wholeNotePixmap.width(), self.wholeNotePixmap.height()),
                                   self.wholeNoteGreenPixmap)
            else:
                painter.drawPixmap(QRect(x, y, self.wholeNotePixmap.width(), self.wholeNotePixmap.height()),
                                   self.wholeNotePixmap)

            #also draw "extra" staff lines on lower and higher notes
            if ind < 7:
                for i in range( int((6-ind) / 2)):
                    if ind%2==0:
                        painter.drawLine(x - 10, y-20*(i) + 10, x + 38, y-20*(i) + 10)
                    else:
                        painter.drawLine(x - 10, y - 20 * (i+1) + 20, x + 38, y - 20 * (i+1) + 20)
            elif ind > 15:
                for i in range( int((ind-14) / 2)):
                    if ind%2 == 0:
                        painter.drawLine(x - 10, y+20*(i) + 10, x + 38, y+20*(i) + 10)
                    else:
                        painter.drawLine(x - 10, y + 20 * (i) + 20, x + 38, y + 20 * (i) + 20)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))

        painter.drawPixmap(QRect(self.offsx,self.offsy, self.clefPixmap.width(), self.clefPixmap.height()), self.clefPixmap)
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        #draw staffs
        for y in range(5):
            painter.drawLine(0, 10+20*y+48+20, self.width, 10+20*y+48+20)

        #draw notes
        self.drawNotes(painter)


class MainWindow(QMainWindow):

    def testtest(self):
        pass

    def __init__(self):
        super().__init__()

        self.gClefWidget = None
        self.fClefWidget = None

        self.gameStarted = False
        self.time = 0.0
        self.time2 = 0.0
        self.numberOfNotesPlayed = 0
        self.timeForLastNote = -1
        self.accuracy = -1
        self.averageTimePerNoteList = []
        self.averageTimePerNote = 0

        self.lasttime = 0
        self.score = 0

        self.sheetLogic = SheetLogic()

        ###set start values###
        # no bass notes
        self.playBass = False
        self.minBassNote = 0
        self.maxBassNote = 0

        # just one treble note at a time
        self.playTreble = True
        self.minTrebleNote = 1
        self.maxTrebleNote = 1

        self.playOnTime = True
        self.playTime = 10  # minutes
        self.unlimitedPlayTime = False

        self.totalNumberOfNotes = 100
        self.unlimitedNumberOfNotes = False

        self.lowestBassNote = 0
        self.highestBassNote = len(fullNotenamesF) - 1

        self.lowestTrebleNote = 0
        self.highestTrebleNote = len(fullNotenamesG) - 1

        self.setupStartUi()

        #repaint UI
        timer = QTimer(self, timeout=self.repaint, interval=100)
        timer.start()

        if midiInputExists:
            self.midiPollingTimer = QTimer(self, timeout=self.midiPolling, interval=100)
        else:
            self.midiPollingTimer = QTimer(self, timeout=self.keyboardPolling, interval=100)

    def keyPressEvent(self, event):

        key = event.key()

        self.sheetLogic.setCharNotePlayed(chr(key))

        if self.sheetLogic.noteInGNoteList(chr(key)) or self.sheetLogic.noteInFNoteList(chr(key)):
            self.handleCorrectNotePressed()

        if self.gClefWidget is not None:
            self.gClefWidget.updateNotes(self.sheetLogic.gClefNotes)
        if self.fClefWidget is not None:
            self.fClefWidget.updateNotes(self.sheetLogic.fClefNotes)

        self.numberOfNotesPlayed += 1
        self.accuracy = 100 * self.score / float(self.numberOfNotesPlayed)


    def handleCorrectNotePressed(self):

        self.lasttime = self.time2 - self.lasttime
        self.timeForLastNote = f"{self.lasttime:.1f} s"
        self.averageTimePerNoteList.append(self.lasttime)

        self.lasttime = 0
        self.time2 = 0

        # self.midiPollingTimer.stop()
        self.repaint()
        self.score += 1
        #time.sleep(.1)

        #ALSO CHECK IF ALL ARE PRESSED
        if self.sheetLogic.allPlayed():
            self.generateNewSheet()


    def generateNewSheet(self):
        self.sheetLogic.generateRandomNotes(self.minBassNote, self.maxBassNote, self.minTrebleNote, self.maxTrebleNote,
                                            self.lowestBassNote, self.highestBassNote,
                                            self.lowestTrebleNote, self.highestTrebleNote)

        if self.gClefWidget is not None:
            #print("updating!!", self.sheetLogic.gClefNotes)
            self.gClefWidget.updateNotes(self.sheetLogic.gClefNotes)
        if self.fClefWidget is not None:
            self.fClefWidget.updateNotes(self.sheetLogic.fClefNotes)

        #generateNewRandomKey()
        #self.gClefWidget.drawGreen = False
        self.midiPollingTimer.start()

    def handleIncorrectNotePressed(self):
        #self.gClefWidget.drawRed = True
        self.midiPollingTimer.stop()
        self.repaint()
        #time.sleep(.5)
        #self.gClefWidget.drawRed = False
        self.midiPollingTimer.start()

    def keyboardPolling(self):
        pass

    def midiPolling(self):
        #print("midipolling")
        #readd = midiInput.read(10)
        #numkeys = 0
        #for r in readd:
        #    if r[0][2]:
        #        numkeys+=1
                #print("key", r[0][1], "\n\n")

        #if numkeys == 3:
        #    print("CHORD!")
        if midiInput.poll():
            midi_events = midiInput.read(10)
            # print "full midi_events " + str(midi_events)
            #print("my midi note is " + str(midi_events[0][0][1]))
            #global keycode
            keycode = midi_events[0][0][1]
            down = midi_events[0][0][2]
            #print(down)

            if keycode >= 36 and keycode <= 96:
                if down:

                    self.numberOfNotesPlayed += 1

                    #if keycode == randomkey:
                    print(keycode, self.sheetLogic.gClefNotes)


                    if self.sheetLogic.keyCodeInGNoteList(keycode):
                        self.sheetLogic.setKeycodeNotePlayed(keycode)
                        self.handleCorrectNotePressed()


                    elif self.sheetLogic.keyCodeInFNoteList(keycode):
                        self.sheetLogic.setKeycodeNotePlayed(keycode)
                        self.handleCorrectNotePressed()

                    else:

                        self.midiPollingTimer.stop()
                        self.repaint()
                        #time.sleep(.5)
                        #self.gClefWidget.drawRed = False
                        self.midiPollingTimer.start()
                    self.accuracy = 100 * self.score / float(self.numberOfNotesPlayed)

    def increaseTime(self):
        self.time += .1
        self.time2 += .1

        timestr = str(datetime.timedelta(seconds=int(self.time)))
        if self.playOnTime:
            timestr += " / " + str(datetime.timedelta(minutes=self.playTime))
        self.totalTimeLabel.setText(timestr)
        if self.accuracy != -1:
            self.accuracyLabel.setText(f"{self.accuracy:.1f}" + " %")
        if self.timeForLastNote != -1:
            self.timeForLastNoteLabel.setText(str(self.timeForLastNote))
        self.numberOfNotesLabel.setText(str(self.numberOfNotesPlayed))

        scorestr = str(self.score)
        if not self.playOnTime:
            scorestr += " / " + str(self.totalnumberOfNotesPlayed)
        self.scoreLabel.setText(scorestr)

        if len(self.averageTimePerNoteList) > 0:
            self.averageTimePerNote = statistics.mean(self.averageTimePerNoteList)

        self.averageTimePerNoteLabel.setText(f"{self.averageTimePerNote : .2f} s")

    def updateValues(self):
        self.playBass = self.bassCheckBox.isChecked()
        self.minBassNote = self.minBassNotesComboBox.currentIndex()
        self.maxBassNote = self.maxBassNotesComboBox.currentIndex()

        self.playTreble = self.trebleCheckBox.isChecked()
        self.minTrebleNote = self.minTrebleNotesComboBox.currentIndex()
        self.maxTrebleNote = self.maxTrebleNotesComboBox.currentIndex()

        self.playOnTime = self.timeRadioButton.isChecked()
        self.playTime = self.timeSpinBox.value()  # minutes
        self.unlimitedPlayTime = self.timeUnlimitedCheckBox.isChecked()

        self.totalNumberOfNotes = self.numberOfNotesSpinBox.value()
        self.unlimitedNumberOfNotes = self.numberOfNotesUnlimitedCheckBox.isChecked()

        self.lowestBassNote = self.lowestBassNoteComboBox.currentIndex()
        self.highestBassNote = self.highestBassNoteComboBox.currentIndex()

        self.lowestTrebleNote = self.lowestTrebleNoteComboBox.currentIndex()
        self.highestTrebleNote = self.highestTrebleNoteComboBox.currentIndex()


    def startGame(self):
        ###gather info from start GUI##
        self.updateValues()

        #generate new sheet of notes with random notes dependent of the choices the user made!
        self.generateNewSheet()

        #if treble is checked, create Widget
        if self.playTreble:
            self.gClefWidget = ClefWidget(self.sheetLogic.gClefNotes, True)
        else:
            self.gClefWidget = None

        #if bass is checked, create Widget
        if self.playBass:
            self.fClefWidget = ClefWidget(self.sheetLogic.fClefNotes, False)
        else:
            self.fClefWidget = None

        self.setupGameUi()
        timer = QTimer(self, timeout=self.increaseTime, interval=100)
        timer.start()
        self.midiPollingTimer.start()
    def quitGame(self):
        self.close()

    def setupGameUi(self):
        self.centralwidget = QtWidgets.QWidget(self)
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
        #self.pausePushButton = QtWidgets.QPushButton(self.centralwidget)
        #self.pausePushButton.setObjectName("pausePushButton")
        #self.gridLayout_2.addWidget(self.pausePushButton, 1, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        #self.clefWidget = ClefWidget()#QtWidgets.QOpenGLWidget(self.centralwidget)
        if self.gClefWidget is not None:
            self.gClefWidget.setObjectName("clefWidget")

        self.clefWidgetGridLayout = QtWidgets.QGridLayout()
        self.clefWidgetGridLayout.setObjectName("clefWidgetGridLayout")

        if self.playTreble:
            self.clefWidgetGridLayout.addWidget(self.gClefWidget, 0, 0, 1, 1)
        if self.playBass:
            self.clefWidgetGridLayout.addWidget(self.fClefWidget, 1, 0, 1, 1)
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
        self.quitPushButton.clicked.connect(self.quitGame)
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
        #self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #self.pausePushButton.setText(_translate("MainWindow", "Pause"))
        self.numberOfNotesGroupBox.setTitle(_translate("MainWindow", "Number of notes"))
        self.scoreGroupBox.setTitle(_translate("MainWindow", "Score"))
        self.scoreDescLabel.setText(_translate("MainWindow", "Score:"))
        self.accuracyDescLabel.setText(_translate("MainWindow", "Accuracy:"))
        self.scoreLabel.setText(_translate("MainWindow", "TextLabel"))
        self.timeGroupBox.setTitle(_translate("MainWindow", "Time"))
        self.timeForLastNoteDescLabel.setText(_translate("MainWindow", "Time for last note:"))
        self.totalTimeDescLabel.setText(_translate("MainWindow", "Total time:"))
        self.averageTimePerNoteDescLabel.setText(_translate("MainWindow", "Average time per note:"))
        self.quitPushButton.setText(_translate("MainWindow", "Quit"))

    def setupStartUi(self):
        self.title = "MidiQuiz"
        self.setObjectName("MainWindow")

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
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.bassGridLayout = QtWidgets.QGridLayout()
        self.bassGridLayout.setContentsMargins(20, 20, 20, 20)
        self.bassGridLayout.setObjectName("bassGridLayout")
        self.minBassNotesComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.minBassNotesComboBox.addItems([str(i) for i in range(5)])
        self.minBassNotesComboBox.setObjectName("minBassNotesComboBox")
        self.bassGridLayout.addWidget(self.minBassNotesComboBox, 2, 0, 1, 1)
        self.maxBassNotesComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.maxBassNotesComboBox.addItems([str(i) for i in range(5)])
        #self.maxBassNotesComboBox.setCurrentIndex(1)
        self.maxBassNotesComboBox.setObjectName("maxBassNotesComboBox")
        self.bassGridLayout.addWidget(self.maxBassNotesComboBox, 2, 1, 1, 1)
        self.numberOfBassNotesToDisplayLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.numberOfBassNotesToDisplayLabel.sizePolicy().hasHeightForWidth())
        self.numberOfBassNotesToDisplayLabel.setSizePolicy(sizePolicy)
        self.numberOfBassNotesToDisplayLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.numberOfBassNotesToDisplayLabel.setObjectName("numberOfBassNotesToDisplayLabel")
        self.bassGridLayout.addWidget(self.numberOfBassNotesToDisplayLabel, 1, 0, 1, 2)
        self.bassCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.bassCheckBox.setFont(font)
        self.bassCheckBox.setObjectName("bassCheckBox")
        self.bassGridLayout.addWidget(self.bassCheckBox, 0, 0, 1, 2)
        self.gridLayout_6.addLayout(self.bassGridLayout, 0, 3, 1, 1)
        self.trebleGridLayout_2 = QtWidgets.QGridLayout()
        self.trebleGridLayout_2.setContentsMargins(20, 20, 20, 20)
        self.trebleGridLayout_2.setObjectName("trebleGridLayout_2")
        self.trebleLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.trebleLabel.sizePolicy().hasHeightForWidth())
        self.trebleLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.trebleLabel.setFont(font)
        self.trebleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.trebleLabel.setObjectName("trebleLabel")
        self.trebleGridLayout_2.addWidget(self.trebleLabel, 0, 0, 1, 2)

        self.highestTrebleNoteComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.highestTrebleNoteComboBox.addItems(fullNotenamesG)
        self.highestTrebleNoteComboBox.setCurrentIndex(self.highestTrebleNote)

        self.highestTrebleNoteComboBox.setObjectName("highestTrebleNoteComboBox")
        self.trebleGridLayout_2.addWidget(self.highestTrebleNoteComboBox, 2, 1, 1, 1)

        self.lowestTrebleNoteComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.lowestTrebleNoteComboBox.addItems(fullNotenamesG)
        self.lowestTrebleNoteComboBox.setObjectName("lowestTrebleNoteComboBox")

        self.trebleGridLayout_2.addWidget(self.lowestTrebleNoteComboBox, 2, 0, 1, 1)
        self.lowestTrebleNoteLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lowestTrebleNoteLabel.sizePolicy().hasHeightForWidth())
        self.lowestTrebleNoteLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lowestTrebleNoteLabel.setFont(font)
        self.lowestTrebleNoteLabel.setObjectName("lowestTrebleNoteLabel")
        self.trebleGridLayout_2.addWidget(self.lowestTrebleNoteLabel, 1, 0, 1, 1)
        self.highestTrebleNoteLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.highestTrebleNoteLabel.sizePolicy().hasHeightForWidth())
        self.highestTrebleNoteLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.highestTrebleNoteLabel.setFont(font)
        self.highestTrebleNoteLabel.setObjectName("highestTrebleNoteLabel")
        self.trebleGridLayout_2.addWidget(self.highestTrebleNoteLabel, 1, 1, 1, 1)
        self.gridLayout_6.addLayout(self.trebleGridLayout_2, 4, 2, 1, 1)
        self.trebleGridLayout = QtWidgets.QGridLayout()
        self.trebleGridLayout.setContentsMargins(20, 20, 20, 20)
        self.trebleGridLayout.setObjectName("trebleGridLayout")
        self.numberOfTrebleNotesToDisplayLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.numberOfTrebleNotesToDisplayLabel.sizePolicy().hasHeightForWidth())
        self.numberOfTrebleNotesToDisplayLabel.setSizePolicy(sizePolicy)
        self.numberOfTrebleNotesToDisplayLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.numberOfTrebleNotesToDisplayLabel.setObjectName("numberOfTrebleNotesToDisplayLabel")
        self.trebleGridLayout.addWidget(self.numberOfTrebleNotesToDisplayLabel, 1, 0, 1, 2)
        self.maxTrebleNotesComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.maxTrebleNotesComboBox.addItems([str(i) for i in range(5)])
        self.maxTrebleNotesComboBox.setCurrentIndex(self.maxTrebleNote)
        self.maxTrebleNotesComboBox.setObjectName("maxTrebleNotesComboBox")
        self.trebleGridLayout.addWidget(self.maxTrebleNotesComboBox, 2, 1, 1, 1)
        self.trebleCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.trebleCheckBox.setFont(font)
        self.trebleCheckBox.setChecked(True)
        self.trebleCheckBox.setObjectName("trebleCheckBox")
        self.trebleGridLayout.addWidget(self.trebleCheckBox, 0, 0, 1, 2)
        self.minTrebleNotesComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.minTrebleNotesComboBox.addItems([str(i) for i in range(5)])
        self.minTrebleNotesComboBox.setCurrentIndex(self.minTrebleNote)
        self.minTrebleNotesComboBox.setObjectName("minTrebleNotesComboBox")
        self.trebleGridLayout.addWidget(self.minTrebleNotesComboBox, 2, 0, 1, 1)
        self.gridLayout_6.addLayout(self.trebleGridLayout, 0, 2, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_6.addWidget(self.line_2, 3, 2, 1, 2)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_6.addWidget(self.line, 1, 2, 1, 2)
        self.numberOfNotesGridLayout = QtWidgets.QGridLayout()
        self.numberOfNotesGridLayout.setContentsMargins(20, 20, 20, 20)
        self.numberOfNotesGridLayout.setObjectName("numberOfNotesGridLayout")
        self.numberOfNotesSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.numberOfNotesSpinBox.setMaximum(10000)
        self.numberOfNotesSpinBox.setValue(self.totalNumberOfNotes)
        self.numberOfNotesSpinBox.setObjectName("numberOfNotesSpinBox")
        self.numberOfNotesGridLayout.addWidget(self.numberOfNotesSpinBox, 1, 0, 1, 1)
        self.notesLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.notesLabel.sizePolicy().hasHeightForWidth())
        self.notesLabel.setSizePolicy(sizePolicy)
        self.notesLabel.setObjectName("notesLabel")
        self.numberOfNotesGridLayout.addWidget(self.notesLabel, 1, 1, 1, 1)
        self.numberOfNotesUnlimitedCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.numberOfNotesUnlimitedCheckBox.sizePolicy().hasHeightForWidth())
        self.numberOfNotesUnlimitedCheckBox.setSizePolicy(sizePolicy)
        self.numberOfNotesUnlimitedCheckBox.setObjectName("numberOfNotesUnlimitedCheckBox")
        self.numberOfNotesGridLayout.addWidget(self.numberOfNotesUnlimitedCheckBox, 1, 2, 1, 1)
        self.numberOfNotesRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.numberOfNotesRadioButton.setFont(font)
        self.numberOfNotesRadioButton.setObjectName("numberOfNotesRadioButton")
        self.numberOfNotesGridLayout.addWidget(self.numberOfNotesRadioButton, 0, 0, 1, 3)
        self.gridLayout_6.addLayout(self.numberOfNotesGridLayout, 2, 3, 1, 1)
        self.bassGridLayout_2 = QtWidgets.QGridLayout()
        self.bassGridLayout_2.setContentsMargins(20, 20, 20, 20)
        self.bassGridLayout_2.setObjectName("bassGridLayout_2")
        self.lowestBassNoteLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lowestBassNoteLabel.sizePolicy().hasHeightForWidth())
        self.lowestBassNoteLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lowestBassNoteLabel.setFont(font)
        self.lowestBassNoteLabel.setObjectName("lowestBassNoteLabel")
        self.bassGridLayout_2.addWidget(self.lowestBassNoteLabel, 1, 0, 1, 1)
        self.bassLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bassLabel.sizePolicy().hasHeightForWidth())
        self.bassLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.bassLabel.setFont(font)
        self.bassLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.bassLabel.setObjectName("bassLabel")
        self.bassGridLayout_2.addWidget(self.bassLabel, 0, 0, 1, 2)
        self.highestBassNoteLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.highestBassNoteLabel.sizePolicy().hasHeightForWidth())
        self.highestBassNoteLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.highestBassNoteLabel.setFont(font)
        self.highestBassNoteLabel.setObjectName("highestBassNoteLabel")
        self.bassGridLayout_2.addWidget(self.highestBassNoteLabel, 1, 1, 1, 1)
        self.lowestBassNoteComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.lowestBassNoteComboBox.addItems(fullNotenamesF)

        self.lowestBassNoteComboBox.setObjectName("lowestBassNoteComboBox")
        self.bassGridLayout_2.addWidget(self.lowestBassNoteComboBox, 2, 0, 1, 1)

        self.highestBassNoteComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.highestBassNoteComboBox.addItems(fullNotenamesF)
        self.highestBassNoteComboBox.setCurrentIndex(self.highestBassNote)
        self.highestBassNoteComboBox.setObjectName("highestBassNoteComboBox")

        self.bassGridLayout_2.addWidget(self.highestBassNoteComboBox, 2, 1, 1, 1)
        self.gridLayout_6.addLayout(self.bassGridLayout_2, 4, 3, 1, 1)
        self.noteRangesLabelGridLayout = QtWidgets.QGridLayout()
        self.noteRangesLabelGridLayout.setObjectName("noteRangesLabelGridLayout")
        self.noteRangesLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.noteRangesLabel.setFont(font)
        self.noteRangesLabel.setObjectName("noteRangesLabel")
        self.noteRangesLabelGridLayout.addWidget(self.noteRangesLabel, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.noteRangesLabelGridLayout, 4, 0, 1, 1)
        self.timeOrNumberOfNotesGridLayout = QtWidgets.QGridLayout()
        self.timeOrNumberOfNotesGridLayout.setObjectName("timeOrNumberOfNotesGridLayout")
        self.timeOrNumberOfNotesLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.timeOrNumberOfNotesLabel.setFont(font)
        self.timeOrNumberOfNotesLabel.setObjectName("timeOrNumberOfNotesLabel")
        self.timeOrNumberOfNotesGridLayout.addWidget(self.timeOrNumberOfNotesLabel, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.timeOrNumberOfNotesGridLayout, 2, 0, 1, 1)
        self.timeGridLayout = QtWidgets.QGridLayout()
        self.timeGridLayout.setContentsMargins(20, 20, 20, 20)
        self.timeGridLayout.setObjectName("timeGridLayout")
        self.minLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.minLabel.sizePolicy().hasHeightForWidth())
        self.minLabel.setSizePolicy(sizePolicy)
        self.minLabel.setObjectName("minLabel")
        self.timeGridLayout.addWidget(self.minLabel, 1, 1, 1, 1)
        self.timeSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.timeSpinBox.setValue(self.playTime)
        self.timeSpinBox.setObjectName("timeSpinBox")
        self.timeGridLayout.addWidget(self.timeSpinBox, 1, 0, 1, 1)
        self.timeUnlimitedCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeUnlimitedCheckBox.sizePolicy().hasHeightForWidth())
        self.timeUnlimitedCheckBox.setSizePolicy(sizePolicy)
        self.timeUnlimitedCheckBox.setObjectName("timeUnlimitedCheckBox")
        self.timeGridLayout.addWidget(self.timeUnlimitedCheckBox, 1, 2, 1, 1)
        self.timeRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.timeRadioButton.setFont(font)
        self.timeRadioButton.setObjectName("timeRadioButton")
        self.timeRadioButton.setChecked(self.playOnTime)
        self.timeGridLayout.addWidget(self.timeRadioButton, 0, 0, 1, 3)
        self.gridLayout_6.addLayout(self.timeGridLayout, 2, 2, 1, 1)
        self.notesToDisplayGridLayout = QtWidgets.QGridLayout()
        self.notesToDisplayGridLayout.setObjectName("notesToDisplayGridLayout")
        self.notesToDisplayLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.notesToDisplayLabel.setFont(font)
        self.notesToDisplayLabel.setObjectName("notesToDisplayLabel")
        self.notesToDisplayGridLayout.addWidget(self.notesToDisplayLabel, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.notesToDisplayGridLayout, 0, 0, 1, 1)
        self.emptyGridLayout = QtWidgets.QGridLayout()
        self.emptyGridLayout.setObjectName("emptyGridLayout")
        self.gridLayout_6.addLayout(self.emptyGridLayout, 5, 0, 1, 1)
        self.startPushButtonGridLayout = QtWidgets.QGridLayout()
        self.startPushButtonGridLayout.setContentsMargins(20, 20, 20, 20)
        self.startPushButtonGridLayout.setObjectName("startPushButtonGridLayout")
        self.startPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.startPushButton.setFocus(True)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startPushButton.sizePolicy().hasHeightForWidth())
        self.startPushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.startPushButton.setFont(font)
        self.startPushButton.setMouseTracking(False)
        self.startPushButton.setFlat(False)
        self.startPushButton.setObjectName("startPushButton")
        self.startPushButton.clicked.connect(self.startGame)
        self.startPushButtonGridLayout.addWidget(self.startPushButton, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.startPushButtonGridLayout, 5, 2, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout_6, 0, 0, 2, 2)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 842, 18))
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
        #self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.numberOfBassNotesToDisplayLabel.setText(
            _translate("MainWindow", "Number of notes to display at a time (min/max):"))
        self.bassCheckBox.setText(_translate("MainWindow", "Bass"))
        self.trebleLabel.setText(_translate("MainWindow", "Treble"))
        self.lowestTrebleNoteLabel.setText(_translate("MainWindow", "Lowest note:"))
        self.highestTrebleNoteLabel.setText(_translate("MainWindow", "Highest note:"))
        self.numberOfTrebleNotesToDisplayLabel.setText(
            _translate("MainWindow", "Number of notes to display at a time (min/max):"))
        self.trebleCheckBox.setText(_translate("MainWindow", "Treble"))
        self.notesLabel.setText(_translate("MainWindow", "notes"))
        self.numberOfNotesUnlimitedCheckBox.setText(_translate("MainWindow", "Unlimited"))
        self.numberOfNotesRadioButton.setText(_translate("MainWindow", "Number of notes"))
        self.lowestBassNoteLabel.setText(_translate("MainWindow", "Lowest note:"))
        self.bassLabel.setText(_translate("MainWindow", "Bass"))
        self.highestBassNoteLabel.setText(_translate("MainWindow", "Highest note:"))
        self.noteRangesLabel.setText(_translate("MainWindow", "Note ranges"))
        self.timeOrNumberOfNotesLabel.setText(_translate("MainWindow", "Time or number of notes?"))
        self.minLabel.setText(_translate("MainWindow", "min"))
        self.timeUnlimitedCheckBox.setText(_translate("MainWindow", "Unlimited"))
        self.timeRadioButton.setText(_translate("MainWindow", "Time"))
        self.notesToDisplayLabel.setText(_translate("MainWindow", "Notes to display"))
        self.startPushButton.setText(_translate("MainWindow", "Start"))

App = QApplication(sys.argv)
window = MainWindow()
sys.exit(App.exec())