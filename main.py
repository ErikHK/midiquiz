
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
        self.startButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.startButton, 1, 0, 1, 1)
        self.startButton.clicked.connect(self.setupGameUi)

        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_4.addWidget(self.label_2, 0, 0, 1, 1)
        self.gridLayout_9 = QtWidgets.QGridLayout()
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setObjectName("label_10")
        self.gridLayout_9.addWidget(self.label_10, 1, 1, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_9.addWidget(self.spinBox, 1, 0, 1, 1)
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout_9.addWidget(self.checkBox_3, 1, 2, 1, 1)
        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout_9.addWidget(self.radioButton, 0, 0, 1, 3)
        self.gridLayout_4.addLayout(self.gridLayout_9, 0, 1, 1, 1)
        self.gridLayout_10 = QtWidgets.QGridLayout()
        self.gridLayout_10.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setObjectName("label_11")
        self.gridLayout_10.addWidget(self.label_11, 1, 1, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout_10.addWidget(self.spinBox_2, 1, 0, 1, 1)
        self.checkBox_4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4.setObjectName("checkBox_4")
        self.gridLayout_10.addWidget(self.checkBox_4, 1, 2, 1, 1)
        self.radioButton_2 = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout_10.addWidget(self.radioButton_2, 0, 0, 1, 3)
        self.gridLayout_4.addLayout(self.gridLayout_10, 0, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_4, 3, 0, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_5.addWidget(self.label_3, 0, 0, 1, 1)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_6.addWidget(self.label_6, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_6.addWidget(self.label_4, 0, 0, 1, 2)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_6.addWidget(self.label_5, 1, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout_6.addWidget(self.comboBox, 2, 0, 1, 1)
        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridLayout_6.addWidget(self.comboBox_2, 2, 1, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_6, 0, 1, 1, 1)
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_8.addWidget(self.label_7, 0, 0, 1, 2)
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout_8.addWidget(self.label_9, 1, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_8.addWidget(self.label_8, 1, 0, 1, 1)
        self.comboBox_3 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_3.setObjectName("comboBox_3")
        self.gridLayout_8.addWidget(self.comboBox_3, 2, 0, 1, 1)
        self.comboBox_4 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_4.setObjectName("comboBox_4")
        self.gridLayout_8.addWidget(self.comboBox_4, 2, 1, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_8, 0, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_5, 6, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.checkBox.setFont(font)
        self.checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_3.addWidget(self.checkBox, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout_3.addWidget(self.checkBox_2, 0, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 4, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_2.addWidget(self.line, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_2.addWidget(self.line_2, 5, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 782, 18))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        #self.setWindowTitle(_translate("self", "MainWindow"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.label_2.setText(_translate("MainWindow", "Time or number of notes?"))
        self.label_10.setText(_translate("MainWindow", "min"))
        self.checkBox_3.setText(_translate("MainWindow", "Unlimited"))
        self.radioButton.setText(_translate("MainWindow", "Time"))
        self.label_11.setText(_translate("MainWindow", "notes"))
        self.checkBox_4.setText(_translate("MainWindow", "Unlimited"))
        self.radioButton_2.setText(_translate("MainWindow", "Number of notes"))
        self.label_3.setText(_translate("MainWindow", "Note ranges"))
        self.label_6.setText(_translate("MainWindow", "Highest note:"))
        self.label_4.setText(_translate("MainWindow", "Bass"))
        self.label_5.setText(_translate("MainWindow", "Lowest note:"))
        self.label_7.setText(_translate("MainWindow", "Treble"))
        self.label_9.setText(_translate("MainWindow", "Highest note:"))
        self.label_8.setText(_translate("MainWindow", "Lowest note:"))
        self.checkBox.setText(_translate("MainWindow", "Treble"))
        self.label.setText(_translate("MainWindow", "Notes to display"))
        self.checkBox_2.setText(_translate("MainWindow", "Bass"))





App = QApplication(sys.argv)
window = MainWindow()
sys.exit(App.exec())
