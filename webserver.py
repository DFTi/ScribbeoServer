import os
import sys
import re
import subprocess
import cherrypy

hidden_names = {
  ".DS_Store":True,
  "Notes":True
}
hidden_exts = {
  ".tc":True
}

def set_rootdir(dir):
  global rootdir
  rootdir = dir
  print "Serving out of "+rootdir
  
### Helpers ###
def unsafe_dirpath(*arg):
  for piece in arg:
    if piece == '..':
      return True
      
def aditc(path):
  zeros = '00:00:00:00'
  if path == None:
    return zeros
  if sys.platform == 'win32':
    return zeros
  script_dir = os.path.dirname(os.path.realpath(__file__))
  aditc = os.path.join(script_dir, 'aditc')
  proc = subprocess.Popen([aditc, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  proc.wait()
  for line in proc.stderr:
    if len(line) > 0:
      return zeros
  for line in proc.stdout:
    timecode = line.rstrip()
    break
  ndftc = re.compile("..:..:..:..")
  # \d{2}:\d{2}:\d{2}:\d{2}
  dftc = re.compile("..:..:..;..")
  if ndftc.match(timecode):
    return timecode[:11]
  elif dftc.match(timecode):
    return timecode[:11].replace(';', ':')
  else:
    return zeros

# FIXME: 
# Some routes, like notes & email are succeptible random filling,
# In a future update, a secret-key should be used between app & server

### CherryPy Server ###
class Routes(object):
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
  def email(self, name=''):
    """ Upload and download notes in email format
        Uploading:    Post request to /email/whatever
                      Writes to {rootdir}/Notes/whatever.html
        Downloading:  Get request to /email/whatever.html
                      Sends {rootdir}/Notes/whatever.html
    """
    note_dir = os.path.join(rootdir, 'Notes')
    path = os.path.join(note_dir, name)
    if cherrypy.request.method == 'GET':
      if os.path.exists(path) and not os.path.isdir(path):
        return cherrypy.lib.static.serve_file(path)
      else:
        return 'Not found on this server.'
    elif cherrypy.request.method == 'POST':
      if not os.path.exists(note_dir):
          os.makedirs(note_dir)
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
      relpath = os.path.join(subdirpath, filename) # .replace(' ', '%20')
      # Check if this is a file or a directory:
      if os.path.isdir(os.path.join(dirpath, filename)):
        entry['list_url'] = '/list/'+relpath
        entries['folders'].append(entry)
      else:
        entry['asset_url'] = '/asset/'+relpath
        entry['note_url'] = '/note/'+relpath
        entry['timecode'] = aditc(os.path.join(dirpath, filename))
        entries['files'].append(entry)
    return entries