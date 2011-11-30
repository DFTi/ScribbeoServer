from distutils.core import setup
import py2exe


setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.1.0",
    description = "Scribbeo Server for Windows",
    name = "ScribbeoServer",

    windows = [
        {"script":"wininit.py"}
        # ,
        # "app.py",
        # "qtwintray/__init__.py",
        # "cherrypy/__init__.py",
        # "bonjour/__init__.py",
        # "aditc/__init__.py"
    ],

    data_files = ['icon.bmp'],

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
