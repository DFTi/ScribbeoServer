from distutils.core import setup
import py2exe
import os
import sys
import shutil
import subprocess

# Path to Nullsoft installer
NSIS = "\"C:\Program Files (x86)\NSIS\makensis.exe\""

exe = False
build = False
for arg in sys.argv:
    if arg == "py2exe":
        exe = True
    if arg == "build":
        build = True
if not exe and not build:
    print "Usage: python setup.py py2exe build"
    sys.exit(0)

if not sys.platform.startswith("win"):
    print "Windows only"
    sys.exit(0)
    
def cleanup():
  expired_files = [
    'dist',
    'build',
    'ScribbeoServerSetup.exe'
  ]
  try:
    for path in expired_files:
      if os.path.exists(path):
        if os.path.isdir(path):
          shutil.rmtree(path)
        else:
          os.remove(path)
  except Exception, ex:
    print "Failed to cleanup "+str(ex)
    sys.exit(1)

print "Cleaning up first."
cleanup()

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.1.1",
    description = "Scribbeo Server for Windows",
    name = "ScribbeoServer",

    windows = [
        {
            "script":"wininit.py",
            "icon_resources":[(1, "icon.ico")]
        },
        "app.py",
    ],

    data_files = [
        'icon.ico',
        'icon.bmp',
        'ScribbeoServerEULA.txt'
    ],

    options = {
        'py2exe':
            {
                "packages":[
                    "encodings"
                ],
                'includes':[
                    'PySide'
                ],
                'bundle_files':1,
                'dll_excludes': [ "mswsock.dll", "powrprof.dll", "MSVCP90.dll", "MSVCR90.dll"]
            },
    })

def renameExecutablesAndVerify():
    if not os.path.exists('dist'):
        return
    for filename in os.listdir("dist"):
        if filename == 'app.exe': # actual server
            os.rename(
                os.path.join('dist',filename),
                os.path.join('dist','ScribbeoServer.exe')
            )
        if filename == 'wininit.exe': # launcher/Gui/Tray
            os.rename(
                os.path.join('dist',filename),
                os.path.join('dist','ScribbeoServerGUI.exe')
            )

    app = os.path.join('dist','ScribbeoServer.exe')
    gui = os.path.join('dist','ScribbeoServerGUI.exe')

    if not os.path.exists(app):
        raise "Missing "+app
    if not os.path.exists(gui):
        raise "Missing "+gui

def copyDLLs():
    shutil.copy("c:\Python27\lib\site-packages\Pythonwin\mfc90.dll",
        os.path.join('dist', 'mfc90.dll'))
    shutil.copy("c:\Python27\DLLs\MSVCP90.dll",
        os.path.join('dist', 'MSVCP90.dll'))

def post_process():
    print "Renaming executables and verifying..."
    renameExecutablesAndVerify()

def makeNSIS():
  print "Creating NSIS installation executable."
  os.system(NSIS+' /V3 make_installer.nsi')
  print "Installer created!"
    
post_process()
makeNSIS()