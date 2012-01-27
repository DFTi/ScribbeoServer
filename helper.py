import os
import sys
import socket
import subprocess
from optparse import OptionParser
win32 = sys.platform.startswith("win")
py2exe = False
if win32 and hasattr(sys, 'frozen'):
  py2exe = True
if win32:
  import winhelper

def make_config(argc, argv):
  parser = OptionParser()
  parser.add_option("-d", dest="dir", help="Location of assets to serve *Required*")
  parser.add_option("-p", dest="port", help="Port for server to bind to")
  parser.add_option("-s", action="store_true", dest="ssl", help="Enable SSL encryption")
  parser.add_option("-c", dest="certdir", help="Directory in which to store SSL certificates")
  parser.add_option("-k", dest="pid", help="Auto shutdown when this PID is lost")
  parser.add_option("-f", dest="ffmpeg", help="Path to compiled ffmpeg")
  parser.add_option("-t", dest="segmenter", help="Path to compiled live segmenter")
  parser.add_option("-n", dest="notes_dir", help="Directory in which to store annotations")
  (options, args) = parser.parse_args()
  options = options.__dict__
  rootdir = validate_directory(options['dir'])
  port = validate_port(options['port'])
  notes_dir = validate_directory(options['notes_dir']) if options['notes_dir'] else None
  ffmpeg = validate_exec(options['ffmpeg']) if options['ffmpeg'] else None
  segmenter = validate_exec(options['segmenter']) if options['segmenter'] else None
  return {
    "port":port,
    "rootdir":rootdir,
    'notes_dir':options['notes_dir'],
    "guipid":options['pid'],
    "ssl":options['ssl'],
    'certdir':options['certdir'],
    'ffmpeg_path':ffmpeg,
    'segmenter_path':segmenter
  }

def make_ssl(config):
  certdir = config['certdir']
  certdir = certdir if certdir else 'certs'
  if not os.path.exists(certdir):
    os.makedirs(certdir)
  certpath = os.path.join(certdir, 'server.cert')
  keypath = os.path.join(certdir, 'server.key')
  if create_https_certificates(certpath, keypath):
    return {
      "cert":certpath,
      "key":keypath
    }
  else:
    return False

def pid_alive(pid):
  if not pid:
    return True
  if win32:
    return winhelper.existsProcessName(pid)
  else: 
    try:
      os.kill(pid, 0) # Send null signal to the PID
      return True
    except OSError:
      return False
    return None

def get_ip_port(testPort=0):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  s.bind((socket.gethostname(), testPort))
  s.listen(1)
  ip, port = s.getsockname()
  s.close()
  return ip, port

def validate_port(port):
  try:
    port = int(port)
  except Exception:
    port
  if not port:
    return get_ip_port()[1]
  elif port < 65535 and port > 0:
    try:
      if get_ip_port():
        return port
    except Exception:
      print "Port is in use. Setting one automatically"
      return get_ip_port()[1]
  else:
    print "Invalid port. Setting one automatically."
    return get_ip_port()[1]

def validate_directory(path):
  if path and os.path.exists(path) and os.path.isdir(path):
    return os.path.abspath(path)
  else:
    if not path:
      print "Missing directory!\nFor help, run "+sys.argv[0]+" -h "
    else:
      print "Invalid directory: "+path
      print "Please create the directory "+path+" and try again."
    sys.exit(-1)

def validate_file(path):
  if path and os.path.exists(path):
    return os.path.abspath(path)
  else:
    print path+" not found!\nFor help, run "+sys.argv[0]+" -h "
    sys.exit(-1)

def validate_exec(path):
  try:
    subprocess.check_call(path)
  except OSError, e:
    print "Invalid path: "+path
    return False
  except subprocess.CalledProcessError, e:
    pass # This is fine, the executable exists.
  return path

def validate_config(config):
  config['ip'] = get_ip_port()[0]
  config['port'] = validate_port(config["port"])
  config['rootdir'] = validate_directory(config["rootdir"])
  return config
    
def disableFrozenLogging():
  # Disable py2exe log feature by routing stdout/sterr to the special nul file
  if win32 and py2exe:
    try:
      sys.stdout = open("nul", "w")
    except:
      print('Failed to close stdout')
    try:
      sys.stderr = open("nul", "w")
    except:
      print('Failed to close stderr')
    

def create_https_certificates(ssl_cert, ssl_key):
    """ Create self-signed HTTPS certificates and store in paths 'ssl_cert' and 'ssl_key'
    """
    try:
        from OpenSSL import crypto
        from certgen import createKeyPair, createCertRequest, createCertificate, TYPE_RSA, serial
    except:
        print 'pyopenssl module missing, please install for https access'
        return False

    # Create the CA Certificate
    cakey = createKeyPair(TYPE_RSA, 1024)
    careq = createCertRequest(cakey, CN='Certificate Authority')
    cacert = createCertificate(careq, (careq, cakey), serial, (0, 60*60*24*365*10)) # ten years

    cname = 'ScribbeoServer'
    pkey = createKeyPair(TYPE_RSA, 1024)
    req = createCertRequest(pkey, CN=cname)
    cert = createCertificate(req, (cacert, cakey), serial, (0, 60*60*24*365*10)) # ten years

    # Save the key and certificate to disk
    try:
        open(ssl_key, 'w').write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
        open(ssl_cert, 'w').write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    except:
        print 'Error creating SSL key and certificate'
        return False

    return True


def shellquote(path):
    return '"'+path+'"' if win32 else path.replace(' ', '\ ')