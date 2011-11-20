#!/usr/bin/python
import app
# Master will store its config here
# It should read this file to see if there's been an initial config.
# In which case, it never needs to write to it again until an UPDATE is made to the App.
# If the app updates a config setting, it should rewrite this file

app.main({
  'port':8080,
  'rootdir':'/Users/keyvan/Code/ScribbeoServer/clips',
  'taskmaster':'ruby' # name of the process we wanna watch for (the guy who calls the python process that calls this script) 
}) # would be sweet to get a PID instead of a task name, but idk how windows compatible that is...