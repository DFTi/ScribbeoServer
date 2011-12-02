from distutils.core import setup
import py2exe
import os
import shutil
import subprocess

def cleanup():
    try:
        shutil.rmtree('dist/')
        shutil.rmtree('build/')
    except:
        pass

print "Cleaning up first."
cleanup()

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.1.0",
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
        'icon.bmp', # yeah we actually need both >.<
        'ScribbeoServerEULA.txt'
    ],

    # Exclude OpenSSL, unless we are building a https server
    #options = { 'py2exe': { 'excludes': 'OpenSSL', "packages": ["encodings", "email"] }},
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
                'dll_excludes': [ "mswsock.dll", "powrprof.dll" ]
            },
    })

def renameExecutablesAndVerify():
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

def main():
    print "Renaming executables and verifying..."
    renameExecutablesAndVerify()
    print "Copying a few dlls..."
    copyDLLs()
    print "Creating the installer..."
    makeNSIS()
    print "Cleaning up."
    cleanup()

NSIS = "C:\Program Files (x86)\NSIS\makensis.exe"

def makeNSIS():
  proc = subprocess.Popen([NSIS, "/V3", "make_installer.nsi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  proc.wait()
    
if __name__ == '__main__':
  main()