#!/usr/bin/env python
import os
import sys
import json
from itty import get, run_itty

serve_dir = os.path.join(os.path.dirname(sys.argv[0]), sys.argv[1])
print "Root directory has been set to "+serve_dir

def send_json(hash):
  Response(json.dumps(hash), content_type='application/json')

@get('/file_listing')
def file_listing(request):
  print "This is the request:\n"
  print request
  print "this is the path:\n"
  print request.GET.get('path')
  return send_json({'foo': 'bar', 'moof': 123})

@get('/')
def index(request):
  print request
  return 'Welcome'

run_itty()