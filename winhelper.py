""" Windows support helper """
import os
import wmi
import requests
import json
import subprocess

c = wmi.WMI()

DATADIR = os.path.join(os.environ['ALLUSERSPROFILE'], 'ScribbeoServer')
SETTINGSFILEPATH = os.path.join(DATADIR, 'settings.json')

def listProcesses():
	for process in c.Win32_Process():
 		print process.ProcessId, process.Name

def existsProcessName(pname):
	for process in c.Win32_Process(name=pname):
 		if process.Name == pname:
 			return True
 	return False

def numberOfProcessesWithName(pname):
	procs = 0
	for process in c.Win32_Process(name=pname):
 		if process.Name == pname:
 			procs = procs+1
 	return procs

def existsProcessID(pid):
	for process in c.Win32_Process(ProcessId=pid):
 		if process.ProcessId == pid:
 			return True
 	return False

def killProcess(pname):
	for process in c.Win32_Process(name=pname):
		process.Terminate()

def bonjourRunning():
	bonjour = "mDNSResponder.exe"
	return existsProcessName(bonjour)

def checkForUpdate(currentVersion, updateURL):
	"""
		Expected JSON from UPDATEURL:
		{
			"version":"1.1",
			"url":"http://path/to/installer"
		}
	"""
	try:
		r = requests.get(updateURL, timeout=1)
		info = json.loads(r.content)
		if info['version'] == currentVersion:
			return False
		else:
			print "found update"
			return info
	except:
		return False
	return False

def needsQuoteWrap(path):
  if not path.startswith('"') and not path.endswith('"'):
    return True
  else:
    return False
