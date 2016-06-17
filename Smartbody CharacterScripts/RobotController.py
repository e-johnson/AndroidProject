import math
import socket 

lastTime =0
#creating a socket connection to the robot
UDP_IP = "192.168.11.2"
UDP_PORT = 2013
sock = socket.socket(socket.AF_INET, #Internet
socket.SOCK_DGRAM) #UDP

class MyController (PythonController):
	#lastTime = 0
	
	def init(self, pawn):
		# setup
		print "Setting up controller..."
		
	def evaluate(self):
		global lastTime
		# run at 30 fps
		curTime = scene.getSimulationManager().getTime()

		if curTime - lastTime < .060 :
			return
		
		eyebrow_left = self.getChannelValue("au_1_left")
		eyebrow_right = self.getChannelValue("au_1_right")
		eyebrow= math.ceil(((eyebrow_left+eyebrow_right)/2) * 100) / 100 

		eyeball_left = self.getChannelQuat("eyeball_left")
		eyeball_pan =  math.ceil(eyeball_left.getData(1) *100)/100
		eyeball_tilt = math.ceil(eyeball_left.getData(2)* 100)/100
		
		eyebrow_knit_left= self.getChannelValue("au_4_left")
		eyebrow_knit_right = self.getChannelValue("au_4_right")
		eyebrow_knit = math.ceil(((eyebrow_knit_left + eyebrow_knit_right)/2) *100)/100 

		eyelid_left = self.getChannelValue("au_45_left")
		eyelid_right = self.getChannelValue("au_45_right")
		eyelid = math.ceil(((eyelid_left + eyelid_right)/2) * 100)/100

		mouth = math.ceil(self.getChannelValue("au_26") * 100)/100
		open_mouth = math.ceil(self.getChannelValue("open")*100)/100
		mouth_corner_left = self.getChannelValue("au_12_left")
		mouth_corner_right = self.getChannelValue("au_12_right")
		mouth_corner = math.ceil(((mouth_corner_left + mouth_corner_right) /2) * 100)/100

		head = self.getChannelQuat("spine5"); 
		headturn = math.ceil(head.getData(1) *100)/100
		necktilt = math.ceil(head.getData(2) *100)/100
		#headnod = math.ceil(head.getData(3) *100)/100 

		#convert Values to the robot coordinate system
		eyebrow_robot = eyebrow * 255
		eyebrow_knit_robot = eyebrow_knit * 255
		eyelid_robot = eyelid * .5 * 255
		eyeball_pan_robot = ((eyeball_pan * -1) +.30) * 425 
		eyeball_tilt_robot = ((eyeball_tilt * -1) +.10) * 1275
		mout_robot = 0
		if(open_mouth > mouth):
			mouth_robot = (open_mouth *255) +40
		else: 
			mouth_robot = mouth *255
		mouth_corner_robot = mouth_corner * 255
		necklean_left_robot = 255 
		necklean_right_robot = 255 
		headturn_robot = (headturn +.15) * 637.5
		if (necktilt < 0): 
			necklean_right_robot = 255 - ((necktilt * -1) * 2550)
		elif (necktilt > 0):
			necklean_left_robot  = 255 - (necktilt * 2550)
		else: 
			necklean_right_robot = 255
			necklean_left_robot = 255

		
 		JointZeroMessage ="set_joint:0:%d" % (eyebrow_robot)
 		JointOneMessage ="set_joint:1:%d" % (eyebrow_knit_robot)
 		JointTwoMessage = "set_joint:2:%d" % (eyelid_robot)
 		JointThreeMessage = "set_joint:3:%d" % (eyeball_pan_robot)
 		JointFourMessage = "set_joint:4:%d" % (eyeball_tilt_robot)
 		JointFiveMessage = "set_joint:5:%d" % (mouth_robot)
 		JointSixMessage = "set_joint:6:%d" % (mouth_corner_robot)
 		JointSevenMessage = "set_joint:7:%d" % (necklean_left_robot)
 		JointEightMessage = "set_joint:8:%d" % (necklean_right_robot)
 		JointNineMessage = "set_joint:9:%d" % (headturn_robot)
 		sock.sendto(JointFiveMessage, (UDP_IP, UDP_PORT))
 		
 		#JointTenMessage = "set_joint:10:%d" % (
 		#JointElevenMessage = "set_joint:11:%d" % (

 			#values converted to robot's value system 
		
		# send some data as a VHMSG. Message name will be 'myrobot', data will be data that was gleaned from channels
		scene.vhmsg2("myrobot", "eyeball_pan: " + str(eyeball_pan_robot) + " eyeball_tilt: " + str(eyeball_tilt_robot)+ "  necktilt_right: " + str(necklean_right_robot) + 
		 "necktilt_left: "+str(necklean_left_robot)+ "headturn:" + str(headturn_robot)+" eyebrow: " + str(eyebrow_robot) + "eyebrow knit: " + str(eyebrow_knit_robot) 
		 + " eyelid:  " + str(eyelid_robot) + " mouth: " + str(mouth_robot) + " mouth corner:" + str(mouth_corner_robot))

		
		
		sock.sendto(JointZeroMessage, (UDP_IP, UDP_PORT))
		sock.sendto(JointOneMessage, (UDP_IP, UDP_PORT))
		sock.sendto(JointTwoMessage, (UDP_IP, UDP_PORT))
		sock.sendto(JointThreeMessage, (UDP_IP, UDP_PORT))
		sock.sendto(JointFourMessage, (UDP_IP, UDP_PORT)) 
		
		
		
		sock.sendto(JointSixMessage, (UDP_IP, UDP_PORT))
		sock.sendto(JointSevenMessage, (UDP_IP, UDP_PORT))
		sock.sendto(JointEightMessage, (UDP_IP, UDP_PORT))
		sock.sendto(JointNineMessage, (UDP_IP, UDP_PORT)) 
		
		
		

		lastTime = curTime
		



myc = MyController()
character = scene.getCharacter('Rachel')
character.setDoubleAttribute("bmlscheduledelay", 0.0)
character.addController(26, myc)
character.setStringAttribute("voice", "audiofile")
character.setStringAttribute("voiceCode", ".")
