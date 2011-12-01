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
    self.On = True
    self.config = helper.validate_config(config)

  def start(self):
    self.start_web_thread()
    self.start_bonjour_thread()
    if self.config.has_key('guipid'):
      self.block(self.config["guipid"])
    else:
      self.block()
    
  def start_web_thread(self):
    self.server = webserver.Webserver(self.config)
    self.web_thread = Thread(target=self.server.start, args=())
    self.web_thread.daemon = True
    self.web_thread.start()
      
  def start_bonjour_thread(self):
    bonjour.On = True
    self.bonjour_thread = Thread(target=bonjour.register, args=(self.config['port'], ))
    self.bonjour_thread.daemon = True
    self.bonjour_thread.start()

  def block(self, pid=None):
    if not pid:
      try:
        while self.On:
          time.sleep(1)
      finally:
        print "Stopping bonjour"
        bonjour.On = False
        self.bonjour_thread.join()
        sys.exit(0)
    else:
      try:
        while helper.pid_alive(pid):
          time.sleep(5)
        print "GUI HAS BEEN LOST -- QUITTING"
      finally:
        sys.exit(0)
      

def main(config=None):
  if not config:
    config = helper.make_config(len(sys.argv), sys.argv)
  App(config).start()
    
if __name__ == '__main__':
  status = main()
  sys.exit(status)