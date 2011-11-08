#!/usr/bin/env python
""" Scribbeo(TM) Server -- Written by Keyvan Fatehi, DigitalFilm Tree, 2011 """

import os
import sys
import subprocess
from threading import Thread
import socket
import select
try:
  import pybonjour
except Exception:
  print "Please install bonjour from http://www.apple.com/support/bonjour/"
  sys.exit(1)
import cherrypy
import re

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

def unsafe_dirpath(*arg):
  for piece in arg:
    if piece == '..':
      return True
      
def aditc(path):
  if path == None:
    return '00:00:00:00'
  script_dir = os.path.dirname(os.path.realpath(__file__))
  aditc = os.path.join(script_dir, 'aditc')
  proc = subprocess.Popen([aditc, path], stdout=subprocess.PIPE)
  proc.wait()
  for line in proc.stdout:
    timecode = line.rstrip()
    break
  pattern = re.compile("..:..:..:..")
  if pattern.match(timecode):
    return timecode[:11]
  else:
    return '00:00:00:00'
  
### CherryPy Server ###
class Server(object):
  @cherrypy.expose
  def index(self):
    return '<center>Welcome to Scribbeo Server!</center>'
  @cherrypy.expose
  def tc(self, *arg): 
    if unsafe_dirpath(*arg):
      return aditc(None)
    path = os.path.join(rootdir, *arg)
    if os.path.exists(path) and not os.path.isdir(path):
      if sys.platform == 'win32':
        return aditc(None) # FIXME : Aditc doesnt work on windows.
      else:
        timecode = aditc(path)
    else:
      return aditc(None)
    return timecode
  @cherrypy.expose
  def note(self, name=''):
    """ Upload and download notes
        Uploading:    Post request to /notes/name_of_archive
                      Writes to {rootdir}/Notes/name_of_archive
        Downloading:  Get request to /notes/name_of_archive
                      Sends {rootdir}/Notes/name_of_archive
        This is succeptible to arbitrary file upload/filling,
        but this server is intended to be run on a trusted LAN.
    """
    note_dir = os.path.join(rootdir, 'Notes')
    path = os.path.join(note_dir, name)
    if cherrypy.request.method == 'GET':
      if os.path.exists(path) and not os.path.isdir(path):
        cherrypy.response.headers['Content-Type'] = 'application/x-gzip'
        return cherrypy.lib.static.serve_file(path)
      else:
        return 'Note not found.'
    elif cherrypy.request.method == 'POST':
      if not os.path.exists(note_dir):
          os.makedirs(note_dir)
      archive = cherrypy.request.body.read()
      file = open(path, 'w')
      file.write(archive)
      file.close()
      return 'Saved'
    else:
      return 'Invalid request.'
  @cherrypy.expose
  def asset(self, *arg):
    if unsafe_dirpath(*arg):
      return 'Invalid URL'
    path = os.path.join(rootdir, *arg)
    if os.path.exists(path) and not os.path.isdir(path):
      return cherrypy.lib.static.serve_file(path)
    else:
      return ''
  @cherrypy.expose
  @cherrypy.tools.json_out()
  def list(self, *arg):
    if unsafe_dirpath(*arg):
      return 'Invalid URL'
    dirpath = os.path.join(rootdir, *arg)
    subdirpath = os.path.join(*arg) if len(arg)>0 else ''
    # Start making the dictionary of content
    entries = {'files':[], 'folders':[]}
    for filename in os.listdir(dirpath):
      name, ext = os.path.splitext(filename)
      if filename in hidden_names:
        continue
      if ext in hidden_exts:
        continue
      entry = {'name':filename, 'ext':ext[1:]}
      relpath = os.path.join(subdirpath, filename)
      # Check if this is a file or a directory:
      if os.path.isdir(os.path.join(dirpath, filename)):
        entry['list_url'] = '/list/'+relpath
        entries['folders'].append(entry)
      else:
        entry['asset_url'] = '/asset/'+relpath
        entry['note_url'] = '/note/'+relpath
        entry['timecode_url'] = '/tc/'+relpath
        entries['files'].append(entry)
    return entries

### Web Server Configure & Start ###
def start_cherrypy(port):
  conf = {
    'global': {
      'server.socket_host': '0.0.0.0',
      'server.socket_port': port
    }
  }
  cherrypy.engine.timeout_monitor.unsubscribe()
  cherrypy.engine.autoreload.unsubscribe()
  cherrypy.quickstart(Server(), '/', conf)    

### Launch our daemons in a new thread ###
def launch(dir, port=None):
  if set_rootdir(dir):
    if port==None:
      ip, port = get_ip_and_port()
    threads = {
      "bonjour":Thread(target=bonjour_register, args=(port, )),
      "cherrypy":Thread(target=start_cherrypy, args=(port, ))
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
def main(dir=None, port=8080):
  if set_rootdir(dir):
    if port==None:
      ip, port = get_ip_and_port()
    Thread(target=bonjour_register, args=(port, ))
    start_cherrypy(port) # Block on cherrypy thread, we're running from console
  return 0
      
if __name__ == '__main__':
  status = main()
  sys.exit(status)
