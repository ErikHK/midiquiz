
import pygame
import pygame.midi
from pygame.locals import *
import math

from pygame import gfxdraw

import random

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal, QTimer)
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
randomkeyindex = random.randint(3, len(allgclefkeys)-1-3)
#randomkeyindex = 3

randomkey = allgclefkeys[randomkeyindex]
print(randomkey, notename[randomkeyindex])

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


def drawNoteAt(painter, x, staffy):
    y = (14-staffy) * 10 + 50
    #painter.rotate(-10)
    #painter.drawEllipse(x, staffy*20+50 + (x/2) * math.sin(19 * math.pi / 180.0), 21, 16)
    painter.drawEllipse(x, y, 20, 16)

    if (staffy < 6. or staffy > 14.) and staffy % 2 == 0:
        painter.drawLine(x-10,y+10, x+30, y+10)

    if staffy < 4.:
        painter.drawLine(x - 10, y + 10-10, x + 30, y + 10-10)

    if staffy > 16.:
        painter.drawLine(x - 10, y + 10+20, x + 30, y + 10+20)

    #painter.rotate(10)
    #painter.restore()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        thread = AThread()
        #thread.finished.connect(app.exit)
        thread.start()


        timer = QTimer(self, timeout=self.repaint, interval=100)
        timer.start()

        self.title = "PyQt5 Drawing Rectangle"
        self.top = 100
        self.left = 100
        self.width = 800
        self.height = 600


        self.InitWindow()


    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()


    def paintEvent(self, e):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)


        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))


        #print("keycode:", keycode)



        #painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        #painter.drawLine(0,0,100,100)
        #painter.drawRect(100, 15, 400,200)

        #draw staff
        for y in range(5):
            painter.drawLine(150, 10+20*y+48, self.width-150, 10+20*y+48)
            #pygame.draw.line(screen, Color_line, (60, 10+10*y+50), (400-60, 10+10*y+50))



        #painter.drawEllipse(200, 200, 21, 14)

        #drawNoteAt(painter, 250, 1)
        #drawNoteAt(painter, 300, 2)
        #drawNoteAt(painter, 350, 3)

        #for y in range(1,11):
        #    drawNoteAt(painter, 100+50*y, y)

        global keycode
        global randomkey
        if keycode == randomkey:
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            global randomkeyindex
            randomkeyindex = random.randint(3, len(allgclefkeys) - 1-3)
            keycode = 0
            randomkey = allgclefkeys[randomkeyindex]
            print( "nytt randomkeyindex:", randomkeyindex)
            print("ny randomkey:", notename[randomkeyindex])
        else:
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))

        drawNoteAt(painter, self.width/2, randomkeyindex)

        #painter.rotate(-10)



#i.close()
#pygame.midi.quit()
#pygame.quit()
#exit()



App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())







Color_screen=(49,150,100)
Color_line=(0,0,0)

pygame.display.set_caption("midi test")
screen = pygame.display.set_mode((400, 300), RESIZABLE, 32)
screen.fill(Color_screen)


going = True

def drawnote(note):
    #pygame.draw.circle(screen, Color_line, (260, 50+note*5), 5)
    gfxdraw.aacircle(screen, 260, 50+note*5, 6, Color_line)


while going:

        pygame.display.flip()
        for y in range(5):
            pygame.draw.line(screen, Color_line, (60, 10+10*y+50), (400-60, 10+10*y+50))
        drawnote(1)
        events = event_get()
        for e in events:
                if e.type in [QUIT]:
                        going = False
                if e.type in [KEYDOWN]:
                        going = False

        if i.poll():
                midi_events = i.read(10)
                #print "full midi_events " + str(midi_events)
                print ("my midi note is " + str(midi_events))
                # convert them into pygame events.
                midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

                for m_e in midi_evs:
                        event_post( m_e )

i.close()
pygame.midi.quit()
pygame.quit()
exit()
#--------------  end miditest.py--------------