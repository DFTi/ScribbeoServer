#!/usr/bin/python
import app
# Master will store its config here
# It should read this file to see if there's been an initial config.
# In which case, it never needs to write to it again until an UPDATE is made to the App.
# If the app updates a config setting, it should rewrite this file
app.main({
  'port':8080,
  'rootdir':'/Users/keyvan/Code/ScribbeoServer/clips',
  'guipid':None # PID of the program launching the script
})