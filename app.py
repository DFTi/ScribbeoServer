import sys
import server
from easygui import *

def get_dir():
  dir = diropenbox("Please choose a folder", "Scribbeo Server")
  if dir == None:
    None
  else:
    msg = "Scribbeo will use this folder: \n"+str(dir)+"\n\nIs this okay?"
    if ccbox(msg):
      return str(dir)
    else:
      None

def check_bonjour():
  try:
    import pybonjour
    return True
  except Exception:
    msg = "Please install bonjour from http://www.apple.com/support/bonjour/"
    msgbox(msg, "Bonjour Missing", "Quit")
    return False

def enter_background_mode():
  while 1:
    if ccbox("Scribbeo Server is running. Would you like to quit?"):
      sys.exit()

def main():
  if check_bonjour():
    dir = get_dir()
    if dir:
      server.launch(dir)
      enter_background_mode()
  else:
    sys.exit(0)
    
main()