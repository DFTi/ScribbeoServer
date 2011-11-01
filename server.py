#!/usr/bin/env python
""" Scribbeo(TM) Server -- Written by Keyvan Fatehi, DigitalFilm Tree, 2011 """

import os
import sys
import thread
import socket
import select
import pybonjour
import cherrypy

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

### CherryPy Server ###
class Server(object):
  @cherrypy.expose
  def index(self):
    return '<center>Welcome to Scribbeo Server!</center>'
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
        entries['files'].append(entry)
    return entries

### Server Starter ###
def start_server(port):
  conf = {
    'global': {
      'server.socket_host': '0.0.0.0',
      'server.socket_port': port
    }
  }
  cherrypy.quickstart(Server(), '/', conf)    
    
### Main Function ###
def main():
  global rootdir
  rootdir = get_rootdir_from_args()
  if rootdir is None:
    print "Pass a valid folder path as an argument to continue. Quitting."
  else:
    ip, port = get_ip_and_port()
    thread.start_new_thread(bonjour_register, (8080, ))
    # I suppose we could also launch the timecode script in another thread too
    # But I don't believe that one is cross-plat
    start_server(8080)
  return 0
    
if __name__ == '__main__':
  status = main()
  sys.exit(status)