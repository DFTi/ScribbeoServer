import server
# Master will store its config here
# It should read this file to see if there's been an initial config.
# In which case, it never needs to write to it again until an UPDATE is made to the App.
# If the app updates a config setting, it should rewrite this file
config = {
  'port':8080,
  'rootdir':None,
  'taskmaster':'ruby' # name of the process we wanna watch for (the guy who calls the python process that calls this script)
}
# If Master does not give a proper port number, we'll just be passing None
server.main(config)