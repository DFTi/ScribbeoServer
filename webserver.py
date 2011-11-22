import os
import sys
import threading
import subprocess
import bonjour
import cherrypy
import aditc
import re

hidden_names = {
  ".DS_Store":True,
  ".bash_history":True,
  "Notes":True
}
hidden_exts = {
  ".tc":True
}

def POST():
  return cherrypy.request.method == 'POST'
def POST():
  return cherrypy.request.method == 'PUT'  
def GET():
  return cherrypy.request.method == 'GET'
  
### Helpers ###
def check_dirpath(*arg):
  for piece in arg:
    if piece == '..':
      raise cherrypy.HTTPError("403 Unsafe directory path")
      
class Webserver(object):
  def __init__(self, config):
    self.app_config = config
    self.rootdir = config["rootdir"]
    self.port = config["port"]
    self.ip = config["ip"], # Just to know the system IP.
    self.web_config = conf = {
      'global': {
        'server.socket_host': '0.0.0.0', # Bind on all interfaces in this version.
        'server.socket_port': config["port"]
      }
    }
    cherrypy.engine.timeout_monitor.unsubscribe()
    cherrypy.engine.autoreload.unsubscribe()
    self.router = self.Router(self.rootdir)
    self.router.owner = self
    self.alive = True
    self.start_bonjour_thread()
    cherrypy.quickstart(self.router, '/', conf)
    
  def start_bonjour_thread(self):
    self.bonjour_thread = threading.Thread(target=bonjour.register, args=(self.port, ))
    self.bonjour_thread.daemon = True
    self.bonjour_thread.start()  
    
  class Router(object):
    def __init__(self, rootdir):
      self.rootdir = rootdir
      self.notedir = os.path.join(rootdir, 'Notes')
      if not os.path.exists(self.notedir):
        os.makedirs(self.notedir)
      
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
      """
      path = os.path.join(self.notedir, name)
      if cherrypy.request.method == 'GET':
        if os.path.exists(path) and not os.path.isdir(path):
          cherrypy.response.headers['Content-Type'] = 'application/x-gzip'
          return cherrypy.lib.static.serve_file(path)
        else:
          return 'Note not found.'
      elif cherrypy.request.method == 'POST':
        archive = cherrypy.request.body.read()
        file = open(path, 'w')
        file.write(archive)
        file.close()
        return 'Saved'
      else:
        return 'Invalid request.'
      
    @cherrypy.expose
    def asset(self, *arg):
      if check_dirpath(*arg):
        return 'Invalid URL'
      path = os.path.join(self.rootdir, *arg)
      if os.path.exists(path) and not os.path.isdir(path):
        return cherrypy.lib.static.serve_file(path)
      else:
        return ''
      
    @cherrypy.expose
    def email(self, name=''):
      """ Upload and download notes in email format
          Uploading:    Post request to /email/whatever
                        Writes to {rootdir}/Notes/whatever.html
          Downloading:  Get request to /email/whatever.html
                        Sends {rootdir}/Notes/whatever.html
      """
      path = os.path.join(self.notedir, name)
      if cherrypy.request.method == 'GET':
        if os.path.exists(path) and not os.path.isdir(path):
          return cherrypy.lib.static.serve_file(path)
        else:
          return 'Not found on this server.'
      elif cherrypy.request.method == 'POST':
        html = cherrypy.request.body.read()
        file = open(path, 'w')
        file.write(html)
        file.close()
        return 'Saved'
      else:
        return 'Invalid request.'
      
    # The next 3 routes are the same in functionality as
    # the 'email' route above. Pure file send/receive.

    @cherrypy.expose
    def audio(self, name=''):
      return self.email(name)

    @cherrypy.expose
    def avid(self, name=''):
      return self.email(name)

    @cherrypy.expose
    def xml(self, name=''):
      return self.email(name)
      
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def list(self, *arg):
      notedir_entries = os.listdir(self.notedir) # Gonna check this out for each file
      check_dirpath(*arg)
      dirpath = os.path.join(self.rootdir, *arg)
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
        relpath = os.path.join(subdirpath, filename) # .replace(' ', '%20')
        # Check if this is a file or a directory:
        abspath = os.path.join(dirpath, filename)
        if os.path.isdir(abspath):
          # Folders
          entry['list_url'] = '/list/'+relpath
          entries['folders'].append(entry)
        else:
          # Files
          entry['asset_url'] = '/asset/'+relpath
          # find out how many note archives we have for this file, + paths, and send
          entry['notes'] = []
          for file in notedir_entries:
            pat = re.compile('\+asset(.*)'+filename+'(.*)')
            if pat.match(file):
              archive_url = os.path.join('/note/'+file)
              entry['notes'].append(archive_url)
          entry['timecode'] = aditc.get(os.path.join(dirpath, filename))
          entries['files'].append(entry)
      return entries
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api(self, *arg):
      if arg[0] == 'config':
        if GET():
          return {
            "alive":self.owner.alive,
            "app_config":self.owner.app_config,
            "web_config":self.owner.web_config
          }
