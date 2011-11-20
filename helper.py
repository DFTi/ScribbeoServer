import os
import sys
import socket

def get_ip_port(testPort=0):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  s.bind((socket.gethostname(), testPort))
  s.listen(1)
  ip, port = s.getsockname()
  s.close()
  return ip, port

def validate_port(port):
  if port and port < 65535 and port > 0:
    try:
      if get_ip_port(port):
        return port
    except Exception:
      print "Port is in use. Setting one automatically"
      return get_ip_port(port)[1]
  else:
    print "Invalid port. Setting one automatically."
    return get_ip_port(port)[1]

def validate_directory(path):
  if path and os.path.exists(path) and os.path.isdir(path):
    return os.path.abspath(path)
  else:
    print "Invalid directory: "+path
    sys.exit(-1)
    
def validate_config(config):
  config['ip'] = get_ip_port()[0]
  config['port'] = validate_port(config["port"])
  config['rootdir'] = validate_directory(config["rootdir"])
  # if taskmaster store grep line or w/e
  return config
    
def make_config(argc, argv):
  ip, port = get_ip_port()
  if argc == 3: # Scriptname, Directory, Port
    port = validate_port(int(argv[2]))
  if argc == 2 or argc == 3:
    rootdir = validate_directory(argv[1])
  else:
    print "Usage: ./server.py path/to/clips [port]"
    sys.exit(-1)
  return {
    "port":port,
    "ip":ip,
    "rootdir":rootdir,
    "taskmaster":None
  }
    