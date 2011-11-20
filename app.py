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
    self.taskmaster_process_check()
      
  def start_web_thread(self):
    self.web_thread = threading.Thread(target=webserver.Webserver, args=(self.config, ))
    self.web_thread.daemon = True
    self.web_thread.start()
      
  def taskmaster_process_check(self):
    if self.config["taskmaster"]:
      while True:
        print "Checking if taskmaster is still alive, for me to still be alive: "+self.config["taskmaster"] 
        time.sleep(5) # just block for now....

def main(config=None):
  if not config:
    config = helper.make_config(len(sys.argv), sys.argv)
  App(config)
    
if __name__ == '__main__':
  status = main()
  sys.exit(status)