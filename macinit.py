#!/usr/bin/python
# This is an example of the file generated & executed by the Mac version
import app
app.main({
  'port':8080,
  'rootdir':'clips', # Where your assets are
  'guipid':None # PID of the program launching the script
  'ssl':False # If set to True, certs will get generated.
  'certdir':'certs', # Where to put generated certs
  'ffmpeg_path':'/path/to/ffmbc', # Use ffmbc, we use it for timecode too
  'segmenter_path':'/path/to/live_segmenter',
  'notes_path':'/path/to/notes'
})