from distutils.core import setup
import py2exe
import os


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

    data_files = ['icon.ico', 'icon.bmp'], # yeah we actually need both >.<

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
                ]
            },
    })

for filename in os.listdir("dist"):
    if filename == 'app.exe':
        os.rename(os.path.join('dist',filename), os.path.join('dist','ScribbeoServer.exe'))
    if filename == 'wininit.exe':
        os.rename(os.path.join('dist',filename), os.path.join('dist','ScribbeoServerGUI.exe')) # <-- thats the launcher.