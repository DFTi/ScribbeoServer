#!/usr/bin/env python
from bottle import route, run

@route('/hello/:name')
def hello(name):
    return '<h1>Hello %s!</h1>' % name.title()

run(host='localhost', port=8080)