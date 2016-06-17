import sys
import inspect, os
import time 
sys.path.append(r'C:\Users\SENRYAKU\Desktop\AndroidProject\vhmsg\vhmsg-py')
import xml.etree.ElementTree as ET

import vhmsg_python
def PrintResult(result):
  print "SUCCESS" if result == 0 else "FAILURE"
def index_containing_substring(the_list, substring):
  for i, s in enumerate(the_list):
    if substring in s:
      return i
  return -1
def vhmsg_callback(string):
  #parses vhmessage xml string to get behavior name 
  print type(string)
  print "check this out"
  a=string.find("<");
  b = string[a:]
  c = b.split(' ')
  #print b
  print c
  print "got to this point man"
  d = c[index_containing_substring(c,'ref')]
  print "err"
  e = d.replace('"','')
  f=e.replace("ref","")
  g=f.replace("=","")
  msgp2 = "<speech ref = \"%s\"" %g
  #msgp1 = r"sb bml.execBML(Brad,
  msgp1 = "sb bml.execBML('Brad','"
  msgp3 = r" />')"
  message = msgp1 +msgp2+msgp3
  print "this is g: "
  print g
  print message
  vhmsg_python.send(message)
  
print "Attempting to connect..."
ret = vhmsg_python.connect("localhost", "DEFAULT_SCOPE", "61616")
PrintResult(ret)

print "Attemping to subscribe..."
ret = vhmsg_python.subscribe("vrExpress")
PrintResult(ret)

print "Attempting to set listener callback..."
ret = vhmsg_python.setListener(vhmsg_callback)

PrintResult(ret)

print "Attempting to wait..."
ret = vhmsg_python.wait(1)
vhmsg_python.send("another message")
PrintResult(ret)
run  = 1
while(run < 100):
	vhmsg_python.wait(10)
	
ret = vhmsg_python.close()
PrintResult(ret)