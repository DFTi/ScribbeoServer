try:
  import pybonjour
except Exception:
  print "Please install bonjour from http://www.apple.com/support/bonjour/"
  sys.exit(-1)
import select
import time

### Bonjour ###
  
def register_callback(sdRef, flags, errorCode, name, regtype, domain):
  if errorCode == pybonjour.kDNSServiceErr_NoError:
    print 'Registered Bonjour service:'
    print '  name    =', name
    print '  regtype =', regtype
    print '  domain  =', domain

def register(port):
  name    = 'videotree'
  regtype = '_videoTree._tcp'
  port    = port
  sdRef = pybonjour.DNSServiceRegister(name = name,
                                       regtype = regtype,
                                       port = port,
                                       callBack = register_callback)
  try:
    try:
      while True:
        ready = select.select([sdRef], [], [])
        if sdRef in ready[0]:
          pybonjour.DNSServiceProcessResult(sdRef)
    except KeyboardInterrupt:
      pass
  finally:
    sdRef.close()