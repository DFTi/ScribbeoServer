from distutils.core import setup
import py2exe

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.1.0",
    description = "Scribbeo Windows Server",
    name = "ScribbeoServer",

    # Exclude OpenSSL, unless we are building a https server
    #options = { 'py2exe': { 'excludes': 'OpenSSL', "packages": ["encodings", "email"] }},
    options = {'py2exe':{"packages":[
        "encodings"
    ]}},
    # targets to build. You may want to make this "windows" rather than
    # "console", to avoid a console window opening. But if you do, you
    # need some way of showing log information
    console = ["app.py",
        "cherrypy/__init__.py",
        "bonjour/__init__.py",
        "aditc/__init__.py"
    ])
