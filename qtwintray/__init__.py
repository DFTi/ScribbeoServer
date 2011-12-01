#!/usr/bin/env python
from PySide import QtCore, QtGui

import systray_rc
import json
import socket
import os 
import sys
import threading
import app

class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()
        self.serverOn = False
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
        self.trayIcon.activated.connect(self.iconActivated)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.messageGroupBox)
        self.setLayout(mainLayout)
        self.trayIcon.show()
        self.setWindowTitle("Scribbeo Server")
        self.resize(400, 100)

    def kill_server(self):
        if self.serverOn:
            self.theApp.On = False
            print "Turned theApp OFF -- please die, I'll join you now."
            self.app_thread.join()
        print "Server is KILLED according to QTWinTray"
        self.serverOn = False

    def start_server(self):
        if self.theApp.On:
            self.kill_server()
        self.app_thread = threading.Thread(target=self.theApp.start)
        self.app_thread.daemon = False
        self.app_thread.start()
        self.serverOn = True

    def startStopServer(self):
        if self.serverOn:
            self.kill_server()
            self.portEdit.setEnabled(True)
            self.dirEditButton.setEnabled(True)
            self.startStopButton.setText("Start")
            self.statusLabel.setText("Server is stopped")            
        else:
            self.port = int(self.portEdit.text())
            problem = self.validate()
            if problem:
                QtGui.QMessageBox.information(self, "Error",
                    problem)
                return
            self.config = {
                'port':self.port,
                'rootdir':self.directory,
            }
            self.theApp = app.App(self.config)
            self.portEdit.setEnabled(False)
            self.dirEditButton.setEnabled(False)
            self.startStopButton.setText("Stop")
            self.start_server()
            self.statusLabel.setText("Server is running: "+self.ip+':'+str(self.port))
            self.updateConfigFile(self.config)

    def loadConfigFile(self):
        if not os.path.exists('settings.json'):
            self.port = None
            self.directory = None
            return
        try:    
            f = open('settings.json', 'r')
            self.config = json.load(f)
            f.close()
            self.port = self.config["port"] 
            self.directory = self.config["rootdir"]
        except:
            pass

    def updateConfigFile(self, config):
        f = open('settings.json', 'w')
        f.write(json.dumps(config))
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

    def closeEvent(self, event):
        return
        if self.trayIcon.isVisible():
            QtGui.QMessageBox.information(self, "Scribbeo Server",
                    "The program will keep running in the system tray. To "
                    "terminate the program, choose <b>Quit</b> in the "
                    "context menu of the system tray entry.")
            self.hide()
            event.ignore()

    def setIcon(self):
        icon = QtGui.QIcon('icon.bmp')
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        self.trayIcon.setToolTip("Server is (status)") # arg was: self.iconComboBox.itemText(index)

    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.hide()
            else:
                self.show()
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def showMessage(self):
        print "ShowMessage called"
        return
        icon = QtGui.QSystemTrayIcon.MessageIcon(
                self.typeComboBox.itemData(self.typeComboBox.currentIndex()))
        self.trayIcon.showMessage(self.titleEdit.text(),
                self.bodyEdit.toPlainText(), icon,
                self.durationSpinBox.value() * 1000)

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

        self.statusLabel = QtGui.QLabel("Server is not running")

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

        messageLayout = QtGui.QGridLayout()
        messageLayout.addWidget(portLabel, 2, 0)
        messageLayout.addWidget(self.portEdit, 2, 1, 1, 4)

        messageLayout.addWidget(dirLabel, 3, 0)
        messageLayout.addWidget(self.dirEditButton, 3, 1, 1, 4)

        messageLayout.addWidget(self.statusLabel, 5, 1)

        messageLayout.addWidget(self.startStopButton, 5, 4)
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

def main(server_app=None):
    app = QtGui.QApplication(sys.argv)
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
        sys.exit(1)
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main();