#!/usr/bin/python

import sys
import os
from PyQt4 import QtGui,QtCore
from optparse import OptionParser

def readNotes(file):
    fid=open(file,'r')
    result={}
    curSlide=-1

    for line in fid:
        if line.lower().find('slide') != -1:
            curSlide=int(line.split()[1])
            result[curSlide]=""
        if line.lower().find('* slide') != -1:
            curSlide=int(line.split()[1])
            result[curSlide]=""
        if curSlide == -1:
            continue
        else:
            result[curSlide]+=line
    return result

#############################
## Info Window             ##
#############################
class InfoWindow(QtGui.QMainWindow):
    def __init__(self, notes, filename):        
        #super(MainApplication,self).__init__()
        QtGui.QDialog.__init__(self)
        self.slideNo=1
        self.filename=filename
        self.notes=notes
        self.hour=0
        self.min=0
        self.sec=0
        self.initUI()   

    def initUI(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SanSerif',10))

        self.setStyleSheet("QLabel { font-size: 24px }")

        self.timer = QtCore.QBasicTimer()

        self.mainWidget = QtGui.QWidget(self)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addStretch(0)
        # timer
        self.timerLbl = QtGui.QLabel('%02d:%02d:%02d'%(self.hour,self.min,self.sec))
        self.timerStartBtn = QtGui.QPushButton("Start")
        self.timerStopBtn = QtGui.QPushButton("Stop")
        self.timerResetBtn = QtGui.QPushButton("Reset")
        self.timerBtnHbox = QtGui.QHBoxLayout()
        self.timerBtnHbox.addWidget(self.timerStartBtn)
        self.timerBtnHbox.addWidget(self.timerStopBtn)
        self.timerBtnHbox.addWidget(self.timerResetBtn)
        self.timerWidgetBtns = QtGui.QWidget(self)
        self.timerWidgetBtns.setLayout(self.timerBtnHbox)

        self.notesLbl = QtGui.QLabel(self.notes[self.slideNo])
        self.notesLbl.resize(self.notesLbl.sizeHint())

        self.ns_pixmap = QtGui.QPixmap(".tmp/"+self.filename+"_"+repr(self.slideNo+1)+".png")
        self.ns_pixmap.scaledToWidth(100)
        self.ns_lbl = QtGui.QLabel(self)
        self.ns_lbl.setPixmap(self.ns_pixmap)
        #self.ns_lbl.resize(self.ns_lbl.minimumSizeHint())

        self.main_hbox = QtGui.QHBoxLayout()
        self.main_hbox.addWidget(self.notesLbl)
        self.main_hbox.addWidget(self.ns_lbl)
        self.main_hbox_widget = QtGui.QWidget(self)
        self.main_hbox_widget.setLayout(self.main_hbox)

        self.vbox.addWidget(self.main_hbox_widget)

        self.vbox.addWidget(self.timerLbl)
        self.vbox.addWidget(self.timerWidgetBtns)

        self.mainWidget.setLayout(self.vbox)
        self.setCentralWidget(self.mainWidget)

        # connections
        self.timerStartBtn.clicked.connect(self.startTimer)
        self.timerStopBtn.clicked.connect(self.stopTimer)
        self.timerResetBtn.clicked.connect(self.resetTimer)

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'),'&Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        nextAction =  QtGui.QAction('&Next',self)
        nextAction.setShortcut(QtCore.Qt.Key_Right)
        nextAction.setStatusTip('Move to Next Slide')
        nextAction.triggered.connect(self.nextSlide)

        prevAction =  QtGui.QAction('&Prev',self)
        prevAction.setShortcut(QtCore.Qt.Key_Left)
        prevAction.setStatusTip('Move to Previous Slide')
        prevAction.triggered.connect(self.prevSlide)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)

        self.toolbar = self.addToolBar('Next')
        self.toolbar.addAction(nextAction)

        self.toolbar = self.addToolBar('Prev')
        self.toolbar.addAction(prevAction)

        self.statusBar().showMessage('Ready')

        self.setGeometry(0,0,500,500)
        self.setWindowTitle('Info Window')
        self.show()

    def startTimer(self):
        sender = self.sender()
        self.timer.start(1000,self)

    def timerEvent(self,event):
        # if event.timerId() == self.timer.timerId():
        # else:
        #     QtGui.QFrame.timerEvent(self, event)
        self.sec += 1
        if self.sec%60 == 0:
            self.min += 1
            self.sec = 0
        if (self.min%60 == 0) and (self.min != 0):
            self.hour += 1
            self.min = 0
        self.timerLbl.setText('<b>%02d:%02d:%02d</b>'%(self.hour,self.min,self.sec))

    def resetTimer(self):
        sender = self.sender()
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.timerLbl.setText('%02d:%02d:%02d'%(self.hour,self.min,self.sec))

    def stopTimer(self):
        self.timer.stop()
        self.timerLbl.setText('%02d:%02d:%02d'%(self.hour,self.min,self.sec))

    def closeEvent(self,event):
        reply = QtGui.QMessageBox.question(self,'Message',
                                           "Quit?",
                                           QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def nextSlide(self):
        sender=self.sender()
        self.presentationWindow.nextSlide()

    def prevSlide(self):
        sender=self.sender()
        self.presentationWindow.prevSlide()

    def addPresWinHandler(self, presWin):
        self.presentationWindow=presWin

#############################
## Presentation Window     ##
#############################
class PresentationWindow(QtGui.QDialog):
    def __init__(self, infoWin):
        QtGui.QDialog.__init__(self,infoWin)
        #self.slideNo = 1
        self.info = infoWin
        self.initUI()
        self.fullScreen = False
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+F"), self, self.toogleFullScreen)
        QtGui.QShortcut(QtGui.QKeySequence("Right"), self, self.nextSlide)
        QtGui.QShortcut(QtGui.QKeySequence("Left"), self, self.prevSlide)

    def initUI(self):
        QtGui.QToolTip.setFont(QtGui.QFont('SanSerif',10))
        
        self.setStyleSheet("QDialog { background-color: Black }")

        self.hbox = QtGui.QHBoxLayout()

        # displaying the slide
        self.pixmap = QtGui.QPixmap(".tmp/"+self.info.filename+"_"+repr(self.info.slideNo)+".png")
        self.lbl = QtGui.QLabel(self)
        self.lbl.setPixmap(self.pixmap)
        self.lbl.resize(self.lbl.sizeHint())
        self.lbl.showFullScreen()
        
        nextAction =  QtGui.QAction('&Next',self)
        nextAction.setShortcut(QtCore.Qt.Key_Right)
        # nextAction.setStatusTip('Move to Next Slide')
        nextAction.triggered.connect(self.nextSlide)

        prevAction =  QtGui.QAction('&Prev',self)
        prevAction.setShortcut(QtCore.Qt.Key_Left)
        # prevAction.setStatusTip('Move to Previous Slide')
        prevAction.triggered.connect(self.prevSlide)

        self.hbox.addWidget(self.lbl)
        self.hbox.setAlignment(QtCore.Qt.AlignHCenter)

        self.setLayout(self.hbox)

        self.setGeometry(30,30,500,500)

        self.setWindowTitle("Presentation")
        self.show()

    def nextSlide(self):
        sender=self.sender()
        self.info.slideNo = self.info.slideNo+1;
        
        # update slide
        self.pixmap = QtGui.QPixmap(".tmp/"+self.info.filename+"_"+repr(self.info.slideNo)+".png")
        self.lbl.setPixmap(self.pixmap)
        self.lbl.resize(self.lbl.sizeHint())

        # update next slide window
        self.info.ns_pixmap = QtGui.QPixmap(".tmp/"+self.info.filename+"_"+repr(self.info.slideNo+1)+".png")
        self.info.ns_lbl.setPixmap(self.info.ns_pixmap)
        #self.info.ns_lbl.resize(self.info.ns_lbl.sizeHint())

        # update status bar
        self.info.statusBar().showMessage('Slide: '+repr(self.info.slideNo))

        # update notes for slide
        if self.info.slideNo in self.info.notes:
            self.info.notesLbl.setText(self.info.notes[self.info.slideNo])
        else:
            self.info.notesLbl.setText("Slide "+repr(self.info.slideNo)+"\n-")

    def prevSlide(self):
        sender=self.sender()
        self.info.slideNo = self.info.slideNo-1;
        
        # update slide
        self.pixmap = QtGui.QPixmap(".tmp/"+self.info.filename+"_"+repr(self.info.slideNo)+".png")
        self.lbl.setPixmap(self.pixmap)
        self.lbl.resize(self.lbl.sizeHint())
        
        # update next slide window
        self.info.ns_pixmap = QtGui.QPixmap(".tmp/"+self.info.filename+"_"+repr(self.info.slideNo+1)+".png")
        self.info.ns_lbl.setPixmap(self.info.ns_pixmap)
        #self.info.ns_lbl.resize(self.info.ns_lbl.sizeHint())

        # update status bar
        self.info.statusBar().showMessage('Slide: '+repr(self.info.slideNo))

        # update notes for slide
        if self.info.slideNo in self.info.notes:
            self.info.notesLbl.setText(self.info.notes[self.info.slideNo])
        else:
            self.info.notesLbl.setText("Slide "+repr(self.info.slideNo)+"\n-")

    def toogleFullScreen(self):
        if not self.fullScreen :
            self.showFullScreen()
        else:
            self.showNormal()
            
        self.fullScreen = not (self.fullScreen)
        
    # this prevents the presentation window from being closed
    def closeEvent(self,event):
        event.ignore()

#############################
## Main                    ##
#############################
def main(filename, notesfile):

    notes=readNotes(notesfile)
        
    print(notes)

    os.system("mkdir .tmp")
    os.system("gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 -sOutputFile=.tmp/"+filename.split(".")[0]+"_%00d.png "+filename)
    
    app = QtGui.QApplication(sys.argv)

    info = InfoWindow(notes, filename.split(".")[0])
    presentation = PresentationWindow(info)
    info.addPresWinHandler(presentation)

    info.raise_()
    presentation.raise_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="PDF file to open")
    parser.add_option("-n", "--notes", dest="notesfile",
                      help="Notes file (default=<pdf file>.txt)")
    (options,args) = parser.parse_args()

    if options.filename == None:
        print('Invalid PDF file')
        exit(1)

    # Check if the actual pdf file exists

    # If notesfile isn't given use <pdf file>.txt
    print('PDF File: '+options.filename)
    if options.notesfile == None:
        options.notesfile = options.filename.split('.')[0]+'.txt'
    
    print('Notes File: '+options.notesfile)
    main(options.filename, options.notesfile)

    # remove the temporary directory
    os.system("rm -Rf .tmp")
