import webservice
import bonjour
import socket
import thread
import sys

rootdir = sys.argv[1];

def get_ip_and_port(testPort=0):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  s.bind((socket.gethostname(), testPort))
  s.listen(1)
  ip, port = s.getsockname()
  s.close()
  return ip, port

def get_two_ports(testPort=0):
  print "Determining IP and locating 2 adjecent open ports."
  try:
    ip, port_one = get_ip_and_port(testPort)
    ip, port_two = get_ip_and_port(port_one+1)
    print "Current IP: "+ip
    print "Available ports: "+str(port_one)+", "+str(port_two)
    return (ip, port_one, port_two)
  except:
    return get_two_ports()

ip, bonjour_port, web_port = get_two_ports()

thread.start_new_thread(bonjour.register, (bonjour_port, ))
webservice.spinup(ip, web_port, rootdir)