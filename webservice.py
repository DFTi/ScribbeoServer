#!/usr/bin/env python
import bonjour
import os
import sys
import thread
from bottle import get, post, put, delete, request, run, static_file

rootdir = ""

hidden_names = {
  ".DS_Store":True,
  "Notes":True
}
hidden_exts = {
  ".tc":True
}

# Allows interface to see assets in the designated folder at path
# Returns a json showing files and folders at path with access URLs
@get('/list')
@get('/list/')
@get('/list/:path#.+#')
def list_assets(path=''):
  dirpath = os.path.join(rootdir, path) if len(path)>0 else rootdir
  entries = {'files':[], 'folders':[]}
  for filename in os.listdir(dirpath):
    name, ext = os.path.splitext(filename)
    if filename in hidden_names:
      continue
    if ext in hidden_exts:
      continue
    entry = {'name':filename, 'ext':ext[1:]}
    relpath = os.path.join(path, filename)
    # Check if this is a file or a directory:
    if os.path.isdir(os.path.join(dirpath, filename)):
      entry['list_url'] = '/list/'+relpath
      entries['folders'].append(entry)
    else:
      entry['asset_url'] = '/asset/'+relpath
      entry['note_url'] = '/note/'+relpath
      entries['files'].append(entry)
  return entries

# Delivers (and streams) assets out of the designated folder
@get('/asset/:path#.+#')
def send_asset(path):
  print "### REQUEST HEADERS ###"
  for header in request.headers:
    print header+" => "+request.headers.get(header)
  return static_file(path, root=rootdir, mimetype='')
  #os.sendfile('/VideoTree/NLA041-Clip4.mov')

@get('/notes/:path')
def send_notes(path):
  return 'ok'
  
@post('/notes/:path')
def receive_notes(path):
  return 'ok'

def spinup(host, port, dir):
  global rootdir
  rootdir = dir
  print "Root directory has been set to "+rootdir
  #run(host=host, port=60581)
  run(host=host, port=port, server='twisted')