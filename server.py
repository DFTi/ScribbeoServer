#!/usr/bin/env python
""" Scribbeo(TM) Server -- Written by Keyvan Fatehi, DigitalFilm Tree, 2011 """

import os
import sys
import subprocess
import threading
import socket
import select
import webserver
try:
  import pybonjour
except Exception:
  print "Please install bonjour from http://www.apple.com/support/bonjour/"
  sys.exit(1)

hidden_names = {
  ".DS_Store":True,
  "Notes":True
}
hidden_exts = {
  ".tc":True
}

### Bonjour ###
def register_callback(sdRef, flags, errorCode, name, regtype, domain):
  if errorCode == pybonjour.kDNSServiceErr_NoError:
    print 'Registered Bonjour service:'
    print '  name    =', name
    print '  regtype =', regtype
    print '  domain  =', domain

def bonjour_register(port):
  name    = 'videotree'
  regtype = '_videoTree._tcp'
  port    = port
  sdRef = pybonjour.DNSServiceRegister(name = name,
                                       regtype = regtype,
                                       port = port,
                                       callBack = register_callback)
  try:
    try:
      while True:
        ready = select.select([sdRef], [], [])
        if sdRef in ready[0]:
          pybonjour.DNSServiceProcessResult(sdRef)
    except KeyboardInterrupt:
      pass
  finally:
    sdRef.close()

### Misc Helpers ###
def get_rootdir_from_args():
  for arg in sys.argv:
    if os.path.exists(arg) and os.path.isdir(arg):
      rootdir = os.path.abspath(arg)
      print "Setting "+rootdir+" as the Scribbeo root directory."
      break
    else:
      rootdir = None
  if rootdir == None:
    print "Please set the directory you wish to serve."
    return False
  else:
    return rootdir
  
def get_ip_and_port(testPort=0):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  s.bind((socket.gethostname(), testPort))
  s.listen(1)
  ip, port = s.getsockname()
  s.close()
  return ip, port

### Web Server Configure & Start ###
def start_cherrypy(port):
  conf = {
    'global': {
      'server.socket_host': '0.0.0.0',
      'server.socket_port': port
    }
  }
  webserver.set_rootdir(rootdir)
  webserver.cherrypy.engine.timeout_monitor.unsubscribe()
  webserver.cherrypy.engine.autoreload.unsubscribe()
  webserver.cherrypy.quickstart(webserver.Routes(), '/', conf)    

### Launch our daemons in a new thread ###
def launch(dir, port=None):
  if set_rootdir(dir):
    if port==None:
      ip, port = get_ip_and_port()
    threads = {
      "bonjour":threading.Thread(target=bonjour_register, args=(port, )),
      "cherrypy":threading.Thread(target=start_cherrypy, args=(port, ))
    }
    for key in threads:
      threads[key].daemon = True # Auto-SIGTERM when main thread terminates
      threads[key].start()
    return threads
  else:
    return False # No root dir.

def set_rootdir(dir):
  global rootdir
  if dir == None:
    rootdir = get_rootdir_from_args()
  else:
    rootdir = dir
  return rootdir

### Main Function ###
def main(dir=None, port=None):
  if len(sys.argv) > 2: # Scriptname, Directory, Port
    port = int(sys.argv[2])
    if port < 65535 and port > 0:
      pass
    else:
      port = None
  if port == None:
    print "Setting random port automatically"
    ip, port = get_ip_and_port()
  if not set_rootdir(dir):
    print "Could not set root directory"
    return 1
  print "Starting services on port: "+str(port)
  bonjourd = threading.Thread(target=bonjour_register, args=(port, ))
  bonjourd.daemon = True
  bonjourd.start()
  start_cherrypy(port) # Block on cherrypy thread, we're running from console
  return 0
      
if __name__ == '__main__':
  status = main()
  sys.exit(status)
  
def foobar():
  print "ah yes we loaded it and ran a method"

#Test