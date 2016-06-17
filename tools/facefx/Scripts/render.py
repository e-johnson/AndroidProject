# This is a general render script that uses ffmpeg.exe.  It requires that you create a 
# "Render" folder in your My Documents/FaceFX Studio 20XX folder, and place ffmpeg.exe
# in there.  You can set console variables to control how the script will behave (what 
# camera to use, if you want to render out one animation, or an entire group, etc.)  
# See the comments below for more info.
from FxStudio import *
from FxAnimation import *
import sys, os, time, math


def getRenderSetting(cvarName, defaultValue):
	retVal = getConsoleVariableImpl(cvarName);
	if None == retVal:
		retVal = defaultValue
		FxStudio.echo("setting console variable " + cvarName + " to " + str(retVal) )
	return retVal

def getRenderSettingOptions(cvarName, defaultValue, options):
	FxStudio.echo("Options for console variable " + cvarName + " include: " + str(options));
	return getRenderSetting(cvarName, defaultValue)

def renderFaceFX():
	# This is the output directory and where ffmpeg.exe is found.
	# You need to create the Render folder manually.
	# This should look something like: My Documents/FaceFX Studio 2010/Render
	# Make sure you have write access to this folder!
	userRenderDir = getConsoleVariable( "g_userdirectory") + "Render\\"

	# ----------------------------------------------------------------------
	# Settings.  These are retrieved from console variables for easy access
	# If no console variable is set, we provide default values. 
	# The getRenderSetting function takes the variable name as the first 
	# parameter and the default value you want to use if the variable is not
	# yet set as the second parameter.
	# ----------------------------------------------------------------------
	outputDirectory = getRenderSetting( "r_outputdir", userRenderDir) 
	if not os.path.exists(outputDirectory):
		outputDirectoryReturn = FxStudio.displayDirectorySelectionDialog('The default render folder ' + outputDirectory + ' did not exist.  Select a Folder for temporary render files.') 
		outputDirectory = str(outputDirectoryReturn) + "\\"
		if None == outputDirectoryReturn:
			raise RuntimeError, "No render folder";
	ffmpegdir = getRenderSetting( "r_ffmpegdir", userRenderDir)
	FFMPEGFilePath = ffmpegdir + "ffmpeg.exe"
	if not os.path.exists(FFMPEGFilePath):
		FFMPEGFilePathReturn = FxStudio.displayFileOpenDialog("Locate FFMPEG.exe.  It is not in the default location.", ffmpegdir, default_filename="ffmpeg.exe", file_must_exist=True) 
		FFMPEGFilePath = str(FFMPEGFilePathReturn)
		if None == FFMPEGFilePathReturn:
			raise RuntimeError, "No ffmpeg.exe";
			
	# we can only render movies if ffmpeg is found.
	renderMode = getRenderSettingOptions( "r_rendermode", "anim", ["anim", "group", "all"])
	FPS = int(getRenderSetting( "r_fps", 20))
	pixelW = int(getRenderSetting( "r_pixelw", 640))
	pixelH = int(getRenderSetting( "r_pixelh", 480))
	# Change these numbers to increase or decrease the quality of the movie.  Higher quality is bigger file size.
	# low quality - qmin = 10, qmax = 51
	# high quality - qmin = 1, qmax = 51
	qmin_setting = float(getRenderSetting( "r_compression_min", 0))
	qmax_setting = float(getRenderSetting( "r_compression_max", 51))
	imageFormat = getRenderSetting( "r_imageformat", "BMP")
	# Change the extension here to render out a different type of movie (AVI, MPG, FLV, WMV, etc.)
	movieFormat = getRenderSetting( "r_movieformat", "AVI")
	
	# The default camera is used by not passing in an argument for the camera.  The default is the 
	# camera selected when you initially open the scene.  Use "Default_Render_Cam" to specify 
	# That nothing should be passed in.
	camera = getRenderSetting( "r_camera", "Default_Render_Cam")
	if camera == "Default_Render_Cam" and len(getCameraNames()) > 0:
		camera = getSingleChoiceFromUser("Choose a camera from which to render:", "Camera Selection", getCameraNames())
		if camera == "":
			camera = "Default_Render_Cam"
	
	facefxFilename = os.path.basename(FxStudio.getActorPath()).replace(".facefx", "")

	# Create the output directory.
	os.system("mkdir " +  "\"" + outputDirectory + "\"")

	screenshotFilename = outputDirectory + facefxFilename + "." + imageFormat


	screenshot_folder = outputDirectory + "__temp__screenshots\\"
	os.system("mkdir " +  "\"" + screenshot_folder + "\"")

	# Add quotes to the exe path
	FFMPEGFilePath = "\"" + FFMPEGFilePath + "\""

	filebase = "fx_render"
	screenshot_file = screenshot_folder + filebase

	selectedGroup = getSelectedAnimGroupName()
	selectedAnim = getSelectedAnimName()
	animationNames = getAnimationNames()
	if getSelectedAnimName() == "" and renderMode == "anim":
		raise RuntimeError, "No animation selected!"
	
	for group in animationNames:
		if (group[0] == selectedGroup) or renderMode == "all":
			for animName in group[1]:
				if (animName == selectedAnim) or renderMode == "all" or renderMode == "group":
					outputFileName = facefxFilename + "_" + group[0] + "_" + animName + "." + movieFormat
					outputMovie = "\"" + outputDirectory + outputFileName + "\""
					selectAnimation(group[0], animName);
					selectedAnim = Animation(group[0], animName);
			
					# Unfortunately, ffmpg's itsoffset isn't working properly by letting us delay the audio by the amount
					# that the animation starts before time 0.  As a result, we need to start at 0, and "chop off" negative 
					# keys.
					#animStartTime = selectedAnim.startTime	
					animStartTime = 0
					animEndTime = selectedAnim.endTime					
				
					offsetTime = -animStartTime;
					
					timestep = 1.0/FPS;
					i = 0
					t = animStartTime
					paddedZeros = "000"
					while t < animEndTime:
						setCurrentTime(t)
						t += timestep
						if i > 9:
							paddedZeros = "00"
						if i > 99:
							paddedZeros = "0"
						if i > 999:
							paddedZeros = ""
						if camera != "Default_Render_Cam":
							issueCommand('render -w "%s" -h "%s" -f "%s" -camera "%s"  -fsaa 1;'%(pixelW, pixelH, screenshot_file + paddedZeros + str(i) + "." + imageFormat, camera))
						else:
							issueCommand('render -w "%s" -h "%s" -f "%s" -fsaa 1;'%(pixelW, pixelH, screenshot_file + paddedZeros + str(i) + "." + imageFormat))
						i += 1
					i -= 1
						

					# replaceing relevant sections with this should work but it doesn't:  imageFormat + "\" -itsoffset " + str(offsetTime) + " -i \""
					# we use "call" to get around a problem with having spaces in the EXE name and argument names discussed here: http://bugs.python.org/issue1524
					command = "call " + FFMPEGFilePath + " -r " + str(FPS) + " -y -f image2 -i " + "\"" + screenshot_file + "%04d." + imageFormat + "\" ";
					if os.path.exists(selectedAnim.absoluteAudioAssetPath):
						# we resample the audio with -ar 22050 because it is required for mp3-based output formates like FLV (11025 and 44100 work as well)
						command += "-i \"" + selectedAnim.absoluteAudioAssetPath + "\" -ar 22050 "
					command += "-vcodec libx264 -qmin " + str(qmin_setting) + " -qmax " + str(qmax_setting) + " -r " + str(FPS) + " " + outputMovie ; 
					if os.system(command) == 1:
						print "ffmpeg failed to convert the file.  Make sure the file is not in use or write protected.  The following is the command that failed:\n" + command
						print "warning: some versions of ffmpeg report audio failure, but actually succeed in converting the audio."
						#raise RuntimeError, "ffmpeg failed to convert the file."
					else:
						FxStudio.echo("Saved file: " + outputMovie);
						#delete screenshot files.  Only match the exact file pattern to avoid deleting important files
					command = "del \"" +screenshot_folder + filebase + "*." + imageFormat + "\"";
					os.system(command)
					
					if renderMode == "anim":
						retVal = getConsoleVariableImpl("r_saveFileName");
						if None == retVal:
							browseDialogFileReturn = FxStudio.displayFileSaveDialog("Move the file to a different location if you prefer.",outputDirectory,  default_filename=outputFileName, wildcard="*."+movieFormat) 
							if None != browseDialogFileReturn:
								browseDialogFile = str(browseDialogFileReturn)
								command = "move " + outputMovie + " \"" + browseDialogFile + "\"";
								os.system(command)
										
	#this will fail if there are any files in it, so it is relatively safe regardless of how careless you get with this script.
	os.rmdir(screenshot_folder)

if getSelectedAnimation()[1] == "":
  errorBox("No animation selected!  This script requires a selected animation to run.")
  raise RuntimeError, "No animation is selected.  Can not run script."
  
if isNoSave():
  errorBox("This script can not be run from the no-save version of FaceFx Studio.  It relies on the render command which saves files.")
  raise RuntimeError, "No-save version can't use render command."
  			
#Do the Render
renderFaceFX();


