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

import numpy
from array import array

class XorMaskerNull:

   def __init__(self, mask = None):
      self.ptr = 0

   def pointer(self):
      return self.ptr

   def reset(self):
      self.ptr = 0

   def process(self, data):
      self.ptr += len(data)
      return data

class XorMaskerSimple:

   def __init__(self, mask):
      assert len(mask) == 4
      self.ptr = 0
      self.mask = mask

   def pointer(self):
      return self.ptr

   def reset(self):
      self.ptr = 0

   def process(self, data):
      dlen = len(data)
      offset = self.ptr & 3
      mask = (self.mask*(dlen/4 + 2))[offset:dlen+offset]
      for i in (8,4,2,1):
        if not dlen % i: break
      if i == 8: dt = numpy.dtype('uint64');
      elif i == 4: dt = numpy.dtype('uint32');
      elif i == 2: dt = numpy.dtype('uint16');
      else: dt = numpy.dtype('B');
      self.ptr += dlen

      return numpy.bitwise_xor(numpy.frombuffer(mask, dtype=dt), numpy.frombuffer(data, dtype=dt)).tostring()


class XorMaskerShifted1:

   def __init__(self, mask):
      assert len(mask) == 4
      self.ptr = 0
      self.mskarray = [array('B'), array('B'), array('B'), array('B')]
      for j in xrange(4):
         self.mskarray[0].append(ord(mask[ j & 3]))
         self.mskarray[1].append(ord(mask[(j + 1) & 3]))
         self.mskarray[2].append(ord(mask[(j + 2) & 3]))
         self.mskarray[3].append(ord(mask[(j + 3) & 3]))

   def pointer(self):
      return self.ptr

   def reset(self):
      self.ptr = 0

   def process(self, data):
      dlen = len(data)
      mask = self.mskarray[self.ptr & 3]
      mask = (mask*(dlen/4 + 2))[:dlen]
      for i in (8,4,2,1):
        if not dlen % i: break
      if i == 8: dt = numpy.dtype('uint64');
      elif i == 4: dt = numpy.dtype('uint32');
      elif i == 2: dt = numpy.dtype('uint16');
      else: dt = numpy.dtype('B');
      self.ptr += dlen

      return numpy.bitwise_xor(numpy.frombuffer(mask, dtype=dt), numpy.frombuffer(data, dtype=dt)).tostring()
