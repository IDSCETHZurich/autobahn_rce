###############################################################################
##
##  Copyright 2012 Tavendo GmbH
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

import sys

from twisted.python import log
from twisted.internet import reactor, defer
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import listenWS

from autobahn.wamp import exportRpc, \
                          WampCraProtocol, \
                          WampServerFactory, \
                          WampCraServerProtocol



class MyServerProtocol(WampCraServerProtocol):
   """
   Authenticating WAMP server using WAMP-Challenge-Response-Authentication ("WAMP-CRA").
   """
   ## our pseudo user/permissions database

   ## auth extra sent by server
   ##
   if True:
      ## when using salted WAMP-CRA, we send salt info ..
      AUTHEXTRA = {'salt': "RANDOM SALT", 'keylen': 32, 'iterations': 1000}
   else:
      AUTHEXTRA = None

   ## secrets by authkey
   ##
   SECRETS = {'foobar': WampCraProtocol.deriveKey('secret', AUTHEXTRA)}

   print "Auth Extra/Secrets"
   print AUTHEXTRA
   print SECRETS

   ## permissions by authkey
   ##
   PERMISSIONS = {'foobar': {'pubsub': [{'uri': 'http://example.com/topics/',
                                         'prefix': True,
                                         'pub': True,
                                         'sub': True}],
                             'rpc': [{'uri': 'http://example.com/procedures/hello',
                                      'call': True}]},
                  None: {'pubsub': [{'uri': 'http://example.com/topics/mytopic1',
                                     'prefix': False,
                                     'pub': False,
                                     'sub': True}],
                         'rpc': []}}

   def onSessionOpen(self):

      ## override global client auth options
      self.clientAuthTimeout = 0
      self.clientAuthAllowAnonymous = True

      ## call base class method
      WampCraServerProtocol.onSessionOpen(self)


   def getAuthPermissions(self, authKey, authExtra):
      ## return permissions which will be granted for the auth key
      ## when the authentication succeeds
      return {'permissions': self.PERMISSIONS.get(authKey, None),
              'authextra': self.AUTHEXTRA}


   def getAuthSecret(self, authKey):
      ## return the auth secret for the given auth key or None when the auth key
      ## does not exist
      secret = self.SECRETS.get(authKey, None)
      if False:
         # we may return the secret as a string ..
         return secret
      else:
         # .. or return a Deferred that when fires provides the secret as a string.
         # This can be used i.e. when you retrieve the secret from a (real) database.
         d = defer.Deferred()
         d.callback(secret)
         return d


   def onAuthenticated(self, authKey, perms):
      ## fired when authentication succeeds

      ## register PubSub topics from the auth permissions
      self.registerForPubSubFromPermissions(perms['permissions'])

      ## register RPC endpoints (for now do that manually, keep in sync with perms)
      if authKey is not None:
         self.registerForRpc(self,
                             'http://example.com/procedures/',
                             [MyServerProtocol.hello])


   @exportRpc("hello")
   def hello(self, name):
      return "Hello back %s!" % name



if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False

   factory = WampServerFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = MyServerProtocol
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
