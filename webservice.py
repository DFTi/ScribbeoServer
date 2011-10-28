#!/usr/bin/env python
import bonjour
import os
import sys
import thread
from bottle import get, post, put, delete, request, run, static_file

rootdir = ""

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
    entry = {'name':name, 'ext':ext}
    relpath = os.path.join(path, filename)
    if len(ext) == 0: # Folder
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
  return static_file(path, root=rootdir)

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
  run(host=host, port=port)
  