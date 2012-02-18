#!/usr/bin/env python
from PySide import QtCore, QtGui

import systray_rc
import json
import socket
import os 
import sys
import subprocess
import winhelper
import time
import helper

# Currently not supporting SSL on the client, so don't show it.
SHOW_SSL = False

DEBUG = False
UPDATEURL = 'http://update.scribbeo.com/windows'
GUI_NAME = 'ScribbeoServerGUI.exe' # this script
VERSION = '1.0'

DATADIR = winhelper.DATADIR
SETTINGSFILEPATH = winhelper.SETTINGSFILEPATH

APP_PATH = os.path.abspath('ScribbeoServer.exe')
FFMPEG_PATH = os.path.abspath('ffmbc.exe')
SEGMENTER_PATH = os.path.abspath('live_segmenter.exe')

UPDATE_CHECK_INTERVAL = helper.hours_to_seconds(24)

if not os.path.exists(APP_PATH) and os.path.exists('app.py'):
    DEBUG = True # Use alternate startup commands for easier debug

class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()
        self.serverOn = False
        self.lastUpdateCheck = None
        self.loadConfigFile()
        # set up the enclosure for Status, Dir, Port, Start/stop btn
        self.createMessageGroupBox() 
        # set up the actions for the tray
        self.createActions()
        # Create the tray icon, bind the actions to it.
        self.createTrayIcon()
        # Set the program window icon
        self.setIcon()
        self.startStopButton.clicked.connect(self.startStopServer)
        self.dirEditButton.clicked.connect(self.dirEditAction)
        self.hideButton.clicked.connect(self.closeEvent)
        self.quitButton.clicked.connect(self.shutdown)

        self.trayIcon.activated.connect(self.iconActivated)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.messageGroupBox)
        
        self.updateNoticeLabel = QtGui.QLabel()
        self.updateNoticeLabel.setOpenExternalLinks(True)
        mainLayout.addWidget(self.updateNoticeLabel)
        
        self.setLayout(mainLayout)
        self.trayIcon.show()
        self.setWindowTitle("Scribbeo Server")
        #self.resize(400, 100)
        self.setFixedSize(450,170)
        self.doBonjourCheck()
        self.startUpdateTimer()


    def startUpdateTimer(self):
      timer = QtCore.QTimer(self)
      self.connect(timer, QtCore.SIGNAL("timeout()"), self.checkForUpdate)
      timer.start(3600)
    
    def checkForUpdate(self):
      theTime = time.time()
      if self.lastUpdateCheck:
        firstCheck = False
        interval = theTime - self.lastUpdateCheck
      else:
        firstCheck = True
        interval = 0.0
      if firstCheck or interval > UPDATE_CHECK_INTERVAL:
        self.updateFound = winhelper.checkForUpdate(VERSION, UPDATEURL)
        if self.updateFound:
          text = str("<a href='"+self.updateFound['url']+"'>Update available: "
                      " Download Scribbeo v"+self.updateFound["version"]+".</a>")
        else:
          text = "Version "+VERSION
        self.updateNoticeLabel.setText(text)
      self.lastUpdateCheck = theTime
      
    def doBonjourCheck(self):
        if not winhelper.bonjourRunning():
            QtGui.QMessageBox.warning(self, "Bonjour Not Detected",
                "Bonjour Print Services could not be found.\n"
                "It is highly recommended that you install Bonjour.\n"
                "Bonjour is required for automatic discovery.\n"
                "It is available for free download from Apple's website")
        
    def kill_server(self):
        if self.serverOn:
            self.app.terminate()
            self.app.wait()
            winhelper.killProcess("live_segmenter.exe")
            winhelper.killProcess("ffmbc.exe")
        self.serverOn = False

    def start_server(self):
        if SHOW_SSL:
            ssl = '-s' if self.sslCheckbox.isChecked() else ''
        else:
            ssl = ''
        if self.serverOn:
            self.kill_server()
        if DEBUG:
            args = ['python', APP_SCRIPT_PATH, '-d', self.directory, '-p', str(self.port), ssl]
        else:
            args = [APP_PATH, '-d', self.directory, '-p', str(self.port), ssl]
            args += ['-f', FFMPEG_PATH, '-t', SEGMENTER_PATH]
        self.app = subprocess.Popen(args, startupinfo=helper.noCmd())
        self.serverOn = True

    def startStopServer(self):
        if not os.path.exists(APP_PATH) and not DEBUG:
            QtGui.QMessageBox.warning(self, "Cannot start the server",
            "Required components could not be found.\n"
            "Please reinstall or contact us for help.")
            return
        if self.serverOn:
            self.kill_server()
            self.portEdit.setEnabled(True)
            self.dirEditButton.setEnabled(True)
            if SHOW_SSL:
                self.sslCheckbox.setEnabled(True)
            self.startStopButton.setText("Start")
            self.statusLabel.setText("Server is stopped")            
        else:
            self.port = int(self.portEdit.text())
            problem = self.validate()
            if problem:
                QtGui.QMessageBox.information(self, "Error", problem)
                return
            self.portEdit.setEnabled(False)
            self.dirEditButton.setEnabled(False)
            if SHOW_SSL:
                self.sslCheckbox.setEnabled(False)
            self.startStopButton.setText("Stop")
            self.start_server()
            self.statusLabel.setText("Server is running: "+self.ip+':'+str(self.port))
            self.updateConfigFile()
        self.trayIcon.setToolTip(self.statusLabel.text()) # Update tooltip with new server status.

    def loadConfigFile(self):
        if not os.path.exists(DATADIR):
            os.makedirs(DATADIR)
        if not os.path.exists(SETTINGSFILEPATH):
            self.port = None
            self.directory = None
            return
        try:    
            f = open(SETTINGSFILEPATH)
            self.config = json.load(f)
            f.close()
            self.port = self.config["port"] 
            self.directory = self.config["rootdir"]
        except:
            pass

    def updateConfigFile(self, dict=None):
        # Get changes
        self.config['port'] = self.port
        self.config['rootdir'] = self.directory
        if dict:
          for key in dict:
            self.config[key] = dict[key]
        # Write to the settings file
        f = open(SETTINGSFILEPATH, 'w')
        f.write(json.dumps(self.config))
        f.close()

    def get_ip_port(self, testPort=0):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind((socket.gethostname(), testPort))
        s.listen(1)
        ip, port = s.getsockname()
        s.close()
        self.ip = ip
        return ip, port

    def validate_port(self, port):
        if port and port < 65535 and port > 0:
            try:
                if self.get_ip_port(port):
                    return port
            except Exception:
                print "Port is in use."
                return False
        else:
            print "Invalid port."
            return False

    def setVisible(self, visible):
        super(Window, self).setVisible(visible)

    def closeEvent(self, event=None):
        if self.trayIcon.isVisible():
            self.showMessage()
            self.hide()
            if event:
                event.ignore()

    def setIcon(self):
        self.icon = icon = QtGui.QIcon('icon.bmp')
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        self.trayIcon.setToolTip(self.statusLabel.text())

    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.checkForUpdate()
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def showMessage(self):
        icon = QtGui.QSystemTrayIcon.Information
        self.trayIcon.showMessage("Scribbeo Server",
            "Scribbeo Server is running in your system tray.\n"
            "Right click the icon to quit the program.", icon,
            5 * 1000)

    def validate(self):
        problem = None
        if not (self.directory and os.path.exists(self.directory)):
            problem = "Invalid directory"
        if not self.validate_port(self.port):
            if problem:
                problem = problem + '\n' + "Invalid port"
            else:
                problem = "Invalid port"
        return problem

    def dirEditAction(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        directory = dialog.getExistingDirectory()
        if directory:
            self.directory = directory
            self.dirEditButton.setText(directory)

    def createMessageGroupBox(self):
        self.messageGroupBox = QtGui.QGroupBox("Settings")

        self.statusLabel = QtGui.QLabel("Server is not currently active.")

        portLabel = QtGui.QLabel("Port:")
        if self.port:
            self.portEdit = QtGui.QLineEdit(str(self.port))        
        else:
            # Default values
            self.portEdit = QtGui.QLineEdit("8080")
            self.port = 8080

        validator = QtGui.QIntValidator(0, 65535, self)
        self.portEdit.setValidator(validator)

        dirLabel = QtGui.QLabel("Folder:")
        if self.directory:
            self.dirEditButton = QtGui.QPushButton(self.directory)
        else:
            self.dirEditButton = QtGui.QPushButton("Choose a directory")

        self.startStopButton = QtGui.QPushButton("Start")
        self.startStopButton.setDefault(True)

        self.hideButton = QtGui.QPushButton("Hide")
        self.quitButton = QtGui.QPushButton("Quit")

        messageLayout = QtGui.QGridLayout()
        messageLayout.addWidget(portLabel, 2, 0)
        messageLayout.addWidget(self.portEdit, 2, 1, 1, 4)

        messageLayout.addWidget(dirLabel, 3, 0)
        messageLayout.addWidget(self.dirEditButton, 3, 1, 1, 4)

        if SHOW_SSL:
            sslLabel = QtGui.QLabel("Use SSL?")
            self.sslCheckbox = QtGui.QCheckBox()        
            messageLayout.addWidget(sslLabel, 4, 0)
            messageLayout.addWidget(self.sslCheckbox, 4, 1, 1, 4)

        messageLayout.addWidget(self.statusLabel, 4, 3, 1, 5)

        messageLayout.addWidget(self.startStopButton, 5, 4)
        messageLayout.addWidget(self.hideButton, 5, 3)
        messageLayout.addWidget(self.quitButton, 5, 2)
        
        # self.updateNoticeLabel = QtGui.QLabel()
        # self.updateNoticeLabel.setOpenExternalLinks(True)
        # messageLayout.addWidget(self.updateNoticeLabel, 0, 3)

        messageLayout.setColumnStretch(3, 1)
        messageLayout.setRowStretch(4, 1)
        self.messageGroupBox.setLayout(messageLayout)

    def createActions(self):
        self.restoreAction = QtGui.QAction("&Open", self,
                triggered=self.showNormal)
        self.quitAction = QtGui.QAction("&Quit", self,
                triggered=self.shutdown)

    def createTrayIcon(self):
         self.trayIconMenu = QtGui.QMenu(self)
         self.trayIconMenu.addAction(self.restoreAction)
         self.trayIconMenu.addSeparator()
         self.trayIconMenu.addAction(self.quitAction)
         self.trayIcon = QtGui.QSystemTrayIcon(self)
         self.trayIcon.setContextMenu(self.trayIconMenu)

    def shutdown(self):
        self.kill_server()
        QtGui.qApp.quit()

    def lock(self):
        self.portEdit.setEnabled(False)
        self.dirEditButton.setEnabled(False)
        self.startStopButton.setEnabled(False)

    def unlock(self):
        self.portEdit.setEnabled(True)
        self.dirEditButton.setEnabled(True)
        self.startStopButton.setEnabled(True)

def main(app=None):
    app = QtGui.QApplication(sys.argv)
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
        sys.exit(1)
    if winhelper.numberOfProcessesWithName("ScribbeoServerGUI.exe") > 1:
        QtGui.QMessageBox.information(None, "Scribbeo Server already running!",
            "You are already running an instance of Scribbeo Server.\n"
            "Check your system tray for the Scribbeo icon")
        sys.exit(1)
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main();