import wmi
c = wmi.WMI()

def listProcesses():
	for process in c.Win32_Process():
 		print process.ProcessId, process.Name

def existsProcessName(pname):
	for process in c.Win32_Process(name=pname):
 		if process.Name == pname:
 			return True
 	return False

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