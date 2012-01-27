import os
import sys
import threading
import subprocess
import cherrypy
import aditc
import re
import helper
import string
import md5
from transcode import Transcoder

hidden = {
  'names':{
    "Notes":True, # Where note archives are saved from iOS app
    "tmp":True, # Where we store transcoded .ts files
    "Thumbs.db":True, # windows junk
    ".DS_Store":True # mac junk
  },
  'exts':{
    ".tc":True # Legacy timecode file. Can delete.
  }
}

### Helpers ###
def check_dirpath(*arg):
  for piece in arg:
    if piece == '..':
      raise cherrypy.HTTPError("403 Unsafe directory path")
      
class Webserver(object):
  def __init__(self, config):
    self.table = {}
    self.app_config = config
    self.rootdir = config["rootdir"]
    self.port = config["port"]
    self.ip = config["ip"], # Just to know the system IP.
    self.web_config = {
      'global': {
        'server.socket_host': '0.0.0.0', # Bind on all interfaces in this version.
        'server.socket_port': self.port,
      }
    }
    if config['ssl']:
      config['ssl'] = helper.make_ssl(config)
      self.web_config['global']['server.ssl_module'] = 'pyopenssl'
      self.web_config['global']['server.ssl_certificate'] = config['ssl']['cert']
      self.web_config['global']['server.ssl_private_key'] = config['ssl']['key']
    
  def start(self):
    cherrypy.engine.timeout_monitor.unsubscribe()
    cherrypy.engine.autoreload.unsubscribe()
    self.router = self.Router(self.app_config)
    self.router.encoder = Transcoder(self.app_config)
    self.router.owner = self
    self.alive = True
    cherrypy.quickstart(self.router, '/', self.web_config)

  class Router(object):
    def __init__(self, config):
      self.rootdir = config['rootdir']
      if config['notes_dir']:
        self.notedir = os.path.abspath(config['notes_dir'])
      else:
        self.notedir = os.path.join(self.rootdir, 'Notes')
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
          cherrypy.response.headers['Content-Type'] = 'application/x-binary'
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
    def asset(self, *arg): # serves static assets
      check_dirpath(*arg)
      path = os.path.join(self.rootdir, *arg)
      if os.path.exists(path) and not os.path.isdir(path):
        return cherrypy.lib.static.serve_file(path)
      else:
        return ''
        
    @cherrypy.expose
    def transcoder(self, *arg): 
      """ live transcode videos, api:
        transcoder/start/path/to/file.mov.m3u8
        transcoder/$hash/$bitrate/segments.m3u8
        transcoder/$hash/$bitrate/$segment.ts
      """
      # FIXME: get paths that have slashes working /transcoder/Cuts/blah/foo.mov
      # CACHE AND PRE TRANSCODE!
      #arg = list(arg)
      fileName, fileExt = os.path.splitext(arg[-1])
      if fileExt == '.m3u8': # Requesting a playlist of segments
        md5hash, bitrate, name = str.split(arg[0], '-')
        cherrypy.response.headers['Content-Type'] = 'application/x-mpegURL'
        # airvideo uses content-type "application/vnd.apple.mpegurl"
        return self.encoder.m3u8_segments_for(md5hash, bitrate)
      elif fileExt == '.ts': # Requesting a segment.
        md5hash, bitrate, seg = str.split(arg[0], '-')
        partPath = self.encoder.segment_path(md5hash, bitrate, os.path.splitext(seg)[0])
        if not partPath:
          raise cherrypy.HTTPError("404 Segment not found")
        else:
          cherrypy.response.headers['Content-Type'] = 'video/MP2T'
          return cherrypy.lib.static.serve_file(partPath)
      else: # Requesting the video as a live transcode session
      # Here
      # replace / with %2f
        check_dirpath(*arg)
        cherrypy.response.headers['Content-Type'] = 'application/x-mpegURL'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=bitrates.m3u8'
        if self.owner.table.has_key(arg[-1]): # Finding based on hash key
          path = self.owner.table[arg[-1]] # Get the video path from the md5key
        else: # Finding based on direct route
          path = os.path.join(self.rootdir, *arg)
        if os.path.exists(path) and not os.path.isdir(path):
          return self.encoder.start_transcoding(path) # Send the available bitrates
        
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
        if filename.startswith('.'):
          continue
        name, ext = os.path.splitext(filename)
        if filename in hidden['names']:
          continue
        if ext in hidden['exts']:
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

          # This line is temporary. For the iOS app, we'll be seeding asset_url
          # accordingly depending if the asset is natively streamable or not.
          md5hash = md5.new(abspath).hexdigest()
          self.owner.table[md5hash] = abspath
          entry['live_transcode'] = '/transcoder/'+md5hash

          entries['files'].append(entry)
      return entries

    @cherrypy.expose
    def timecode(self, *arg): # Return timecode for asset
      notedir_entries = os.listdir(self.notedir)
      if arg[0] == 'asset':
        arg = arg[1:]
      check_dirpath(*arg)
      path = os.path.join(self.rootdir, *arg)
      if os.path.exists(path) and not os.path.isdir(path):
        return aditc.ffmbc_tc(path, self.owner.app_config['ffmpeg_path'])
      else:
        return '00:00:00:00'
          
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def notes(self, *arg): # Return a JSON of notes' urls
      notedir_entries = os.listdir(self.notedir)
      if arg[0] == 'asset':
        arg = arg[1:]
      check_dirpath(*arg)
      path = os.path.join(self.rootdir, *arg)
      filename = arg[-1]
      urls = []
      if os.path.exists(path) and not os.path.isdir(path):
        for file in notedir_entries:
          pat = re.compile('\+asset(.*)'+filename+'(.*)')
          if pat.match(file):
            archive_url = os.path.join('/note/'+file)
            urls.append(archive_url)
      return urls
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api(self, *arg):
      if arg[0] == 'config':
        if cherrypy.request.method == 'GET':
          return {
            "alive":self.owner.alive,
            "app_config":self.owner.app_config,
            "web_config":self.owner.web_config
          }
