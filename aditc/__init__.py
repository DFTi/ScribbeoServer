import os
import sys
from subprocess import Popen, PIPE
import re

zeros = '00:00:00:00'
ndftc_pattern = re.compile("timecode: \d{2}:\d{2}:\d{2};\d{2}")
dftc_pattern = re.compile("timecode: \d{2}:\d{2}:\d{2}:\d{2}")

def ffmbc_tc(vidPath, ffmbcPath):
  if vidPath == None:
    return zeros
  proc = Popen([ffmbcPath, '-i', vidPath], stderr=PIPE)
  proc.wait()
  output = proc.stderr.read()
  ndftc = ndftc_pattern.search(output)
  if ndftc:
    return ndftc.group()[10:]
  dftc = dftc_pattern.search(output)  
  if dftc:
    return dftc.group()[10:].replace(';', ':')
  return zeros
  