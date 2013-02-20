###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################
import os
import sys
import subprocess

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist

LONGSDESC = """
Twisted-based WebSocket/WAMP client and server framework.
Optimised with routies for faster numpy based masks and deferrd support for the RoboEarth Cloud Engine

AutobahnPython provides a WebSocket (RFC6455, Hybi-10 to -17, Hixie-76)
framework for creating WebSocket-based clients and servers. 
Optimised with routies for faster numpy based masks and deferrd api. 

AutobahnPython also includes an implementation of WAMP
(The WebSockets Application Messaging Protocol), a light-weight,
asynchronous RPC/PubSub over JSON/WebSocket protocol.

More information:

   * http://autobahn.ws/python
   * http://wamp.ws
   * http//www.roboearth.org

Source Code:

   * https://github.com/dhananjaysathe/AutobahnPython
"""

## get version string from "autobahn/_version.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahn/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

class NoCython(Exception):
    pass

def cythonize(src):
    sys.stderr.write("cythonize: %r\n" % (src,))
    subprocess.check_call("cython '%s'" % (src,), shell=True)

def ensure_source(src):
    pyx = os.path.splitext(src)[0] + '.pyx'
    if not os.path.exists(src) \
       or os.stat(src).st_mtime < os.stat(pyx).st_mtime:
        cythonize(pyx)
    return src

class BuildExt(build_ext):
    def build_extension(self, ext):
        try:
            ext.sources = list(map(ensure_source, ext.sources))
        except NoCython:
            print("Cython is required for building extension from checkout.")
            print("Install Cython >= 0.16 ")
            raise
        return build_ext.build_extension(self, ext)

class Sdist(sdist):
    def __init__(self, *args, **kwargs):
        cythonize('autobahn/utf8validator.pyx')
        sdist.__init__(self, *args, **kwargs)

ext_modules = [
    Extension('autobahn.utf8validator', ['autobahn/utf8validator.c']),
    ]
setup (
   name = 'autobahn',
   version = verstr,
   description = 'AutobahnPython - Optimised and modified for the RoboEarth Cloud Engine.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Dhananjay Sathe',
   author_email = 'dhananjaysathe@gmail.com',
   url = 'https://github.com/dhananjaysathe/AutobahnPython',
   platforms = ('Any'),
   install_requires = ['setuptools', 'Twisted>=11.1', 'numpy'],
   packages = ['autobahn'],
   cmdclass={'build_ext': BuildExt, 'sdist': Sdist},
   ext_modules=ext_modules,
   zip_safe = False,
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Software Development :: Libraries"],
   keywords = 'autobahn rapyuta autobahn.ws websocket realtime rfc6455 wamp rpc pubsub'
)
