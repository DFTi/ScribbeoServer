#!/usr/bin/env python
""" Scribbeo(TM) Server -- Written by Keyvan Fatehi, DigitalFilm Tree, 2011 """
import os
import sys
import time
from threading import Thread
import webserver
import bonjour
import helper

class App(object):
  def __init__(self, config):
    self.config = helper.validate_config(config)
    self.server = webserver.Webserver(self.config)

  def start(self):
    self.start_web_thread()
    if bonjour.On:
      self.start_bonjour_thread()
    self.block()
    
  def start_web_thread(self):
    self.web_thread = Thread(target=self.server.start, args=())
    self.web_thread.daemon = True
    self.web_thread.start()
      
  def start_bonjour_thread(self):
    self.bonjour_thread = Thread(target=bonjour.register, args=(self.config['port'], ))
    self.bonjour_thread.daemon = True
    self.bonjour_thread.start()

  def block(self, pid=None):
    if helper.win32 and helper.py2exe:
      pid = "ScribbeoServerGUI.exe"
    else:
      if self.config.has_key("guipid"):
        pid = self.config['guipid']
      else:
        pid = None
    try:
      while helper.pid_alive(pid):
        time.sleep(5)
    finally:
      self.shutdown()
  
  def shutdown(self):
    print "Shutting down!"
    print "Stopping bonjour"
    if bonjour.On:
      bonjour.On = False
      self.bonjour_thread.join()
    print "Stopping web thread"
    webserver.cherrypy.process.bus.exit()
    # Annoying. Just quit.      

def main(config=None):
  #helper.disableFrozenLogging()
  if not config:
    config = helper.make_config(len(sys.argv), sys.argv)
  App(config).start()
    
if __name__ == '__main__':
  status = main()
  sys.exit(status)