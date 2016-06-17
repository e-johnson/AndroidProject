
import os,sys
folder = 'C:\Users\SENRYAKU\Documents\SmartBody\data\sounds'
for filename in os.listdir(folder):
       infilename = os.path.join(folder,filename)
       if not os.path.isfile(infilename): continue
       oldbase = os.path.splitext(filename)
       newname = infilename.replace('.bml.txt', '.bml')
       output = os.rename(infilename, newname)