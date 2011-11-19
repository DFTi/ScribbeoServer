#!/usr/bin/env python
""" Scribbeo(TM) Server -- Written by Keyvan Fatehi, DigitalFilm Tree, 2011 """

import sys
import threading
import bonjour
import webserver
import helper

class App(object):
  def __init__(self, config):
    self.config = config
    webserver.start(config)
    self.do_keep_alive()
    
  def weave_threads(self):
    threads = {
      "bonjour":threading.Thread(target=bonjour.register, args=(self.config["port"], )),
      "cherrypy":threading.Thread(target=webserver.serve, args=(self.config["port"], ))
    }
    for key in threads:
      threads[key].daemon = True # Auto-SIGTERM when main thread terminates
      threads[key].start()
    return threads
      
  def do_keep_alive(self):
    import time
    while True:
      print "keepalive blocking call... replace me with service check for "+config["master"] 
      time.sleep(5)

def main(config=None):
  app = App()  
  if config["taskmaster"]
    print "Running in taskmaster mode under "+config["taskmaster"]
  config = helper.make_config(len(sys.argv), sys.argv)
  app.config = 
    
if __name__ == '__main__':
  status = main()
  sys.exit(status)