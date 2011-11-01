import webservice
import bonjour
import socket
import thread
import sys
import os

def get_rootdir_from_args():
  for arg in sys.argv:
    if os.path.exists(arg) and os.path.isdir(arg):
      print "Directory passed in: "+arg
      rootdir = arg
      print "Setting "+arg+" as the Scribbeo root directory."
      break
    else:
      rootdir = None
  return rootdir
  
def get_ip_and_port(testPort=0):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  s.bind((socket.gethostname(), testPort))
  s.listen(1)
  ip, port = s.getsockname()
  s.close()
  return ip, port

def get_ip_and_two_ports(testPort=0):
  print "Determining IP and locating 2 adjecent open ports."
  try:
    ip, port_one = get_ip_and_port(testPort)
    ip, port_two = get_ip_and_port(port_one+1)
    print "Current IP: "+ip
    print "Available ports: "+str(port_one)+", "+str(port_two)
    return (ip, port_one, port_two)
  except:
    return get_ip_and_two_ports()

def spinup():
  rootdir = get_rootdir_from_args()
  if rootdir is None:
    print "Pass a valid folder path as an argument to continue. Quitting."
    return
  else:
    ip, bonjour_port, web_port = get_ip_and_two_ports()
    thread.start_new_thread(bonjour.register, (bonjour_port, ))
    # I suppose we could also launch the timecode script in another thread too
    # But I don't believe that one is cross-plat
    webservice.spinup(ip, web_port, rootdir)
    
spinup()