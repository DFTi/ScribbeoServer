#!/usr/bin/env python
""" Scribbeo(TM) Server -- Written by Keyvan Fatehi, DigitalFilm Tree, 2011 """

import sys
import time
import threading
import webserver
import helper

class App(object):
  def __init__(self, config):
    self.config = helper.validate_config(config)
    self.start_web_thread()
    self.block(self.config["guipid"])
    
  def start_web_thread(self):
    self.web_thread = threading.Thread(target=webserver.Webserver, args=(self.config, ))
    self.web_thread.daemon = True
    self.web_thread.start()
      
  def block(self, pid):
    if not pid:
      try:
        while True:    
          time.sleep(60)
      finally:
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
  App(config)
    
if __name__ == '__main__':
  status = main()
  sys.exit(status)