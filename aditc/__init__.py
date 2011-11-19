import os
import sys
import subprocess
import re

def get(path):
  zeros = '00:00:00:00'
  if path == None:
    return zeros
  if sys.platform == 'win32':
    return zeros
  script_dir = os.path.dirname(os.path.realpath(__file__))
  aditc = os.path.join(script_dir, 'aditc')
  proc = subprocess.Popen([aditc, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  proc.wait()
  for line in proc.stderr:
    if len(line) > 0:
      return zeros
  for line in proc.stdout:
    timecode = line.rstrip()
    break
  ndftc = re.compile("..:..:..:..")
  # \d{2}:\d{2}:\d{2}:\d{2}
  dftc = re.compile("..:..:..;..")
  if ndftc.match(timecode):
    return timecode[:11]
  elif dftc.match(timecode):
    return timecode[:11].replace(';', ':')
  else:
    return zeros