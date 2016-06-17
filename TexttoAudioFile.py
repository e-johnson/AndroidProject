
import sys
import inspect, os,time, shutil
sys.path.append(r'vhmsg\vhmsg-py')
import vhmsg_python
vhmsg_python.connect("localhost", "DEFAULT_SCOPE", "61616")


file = open('utterances.txt', 'r')
for line in file:
	linesplit = line.split("\t")
	a = linesplit[1]
	# we take all characters in the file except the last because on some systems it creates a new line between the file name and .wav extention
	filename = a[0:(len(a)-1)]
	audiofilename = "%s.wav" %filename
	textfile = "C:\Users\SENRYAKU\Documents\SmartBody\data\sounds\%s.txt"%filename
	
	
	if not os.path.exists(os.path.dirname(textfile)):
		try:
			os.makedirs(os.path.dirname(textfile))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise
	with open(textfile, "w") as f:
		f.write(linesplit[0])
	
	
	print " %s" %audiofilename
	print "Attempting to send..."
	vhmsg_python.send("RemoteSpeechCmd speak ChrBrad 1 Microsoft|Zira|Desktop ../../data/cache/audio/utt_20121109_153323_ChrBrad_1.aiff <?xml version=\"1.0\" encoding=\"utf-16\"?><speech id=\"sp1\" ref=\"Anybody-1\" type=\"application/ssml+xml\"> %s </speech>" % linesplit[0])
	vhmsg_python.wait(15)
	print "check this out"
	
	shutil.move(r"C:\vhtoolkit\data\cache\audio\utt_20121109_153323_ChrBrad_1.wav", r"C:\Users\SENRYAKU\Documents\SmartBody\data\sounds\%s" %audiofilename)
print audiofilename 
