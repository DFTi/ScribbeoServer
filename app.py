import sys
import server
from easygui import *

def get_dir_by_dialog():
  dir = diropenbox("Please choose a folder", "Scribbeo Server")
  if dir == None:
    None
  else:
    msg = "Scribbeo will use this folder: \n"+str(dir)+"\n\nIs this okay?"
    if ccbox(msg):
      return str(dir)
    else:
      None

def has_bonjour():
  try:
    import pybonjour
    return True
  except Exception:
    msg = "Please install bonjour from http://www.apple.com/support/bonjour/"
    msgbox(msg, "Bonjour Missing", "Quit")
    return False

def start_and_block(dir):
  server.launch(dir) # Start the server on an alternate thread.
  msg = "Scribbeo Server is now running!\nYou may minimize "
  msg += "this window and use Scribbeo on your networked iDevices"
  msgbox(msg, ok_button="Quit") # And block this thread.

def get_dir():
  dir = server.get_rootdir_from_args() # Drag and drop support
  if dir:
    return dir
  else:
    return get_dir_by_dialog()

def main():
  if not has_bonjour():
    sys.exit(0)
  else:
    dir = get_dir()
    if dir:
      start_and_block(dir)

main()