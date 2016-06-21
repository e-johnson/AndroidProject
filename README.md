# Android Project 
This dcoument provides instructions on how to  install and run the components needed to control the android robot using the Virtual Human Toolkit


## Installing the System 
The first step is to install the virtual human toolkit, it's 3rd party dependencies, and smartbody.
The toolkit comes with a version of smartbody, but that smarbody version is imcompatible with the current system set up 
[Download Installer Here:] (https://www.dropbox.com/sh/kwj3j6y6j8b0s4z/AADdTkipPNo22SrxKRqxfDd6a?dl=0)

By default, smartbody should be installed in your Document directory and the vhtoolkit in the C: directory. 

Once you have smartbody and the vhtoolkit installed, download the Android Github project. you can place it anywhere. 

Open the run-toolkit-sbgui-monitor.bat file  
 ```
 C:\vhtoolkit\bin\launcher-scripts\run-toolkit-sbgui-monitor.bat
 ```
 and change the first line to point to the bin folder of your Smartbody install. For example, on the current machine, Smartbody is located in the documents folder and the first lines of the run-toolkit-sbgui-monitor.bat looks like this 
 ```
 @pushd C:\Users\SENRYAKU\Documents\SmartBody\bin
 ```
 Also, make sure to add the robot.plist file in the Android Project folder to the classifier folder:
 ```
 C:\vhtoolkit\data\classifier
 ```
 
 Create a directory called sounds in the data directory of Smartbody. This is were you will store your audio and bml files. 
 
From these steps, your system should be able to launch and run without a problem. 
 
 
##Running the Full System. 
 To run the system, you can execute the run-launcher.bat file. located in the AndroidProject folder. There is also a version of this script in the vhtoolkit directory which works just as fine. 
 Once the launcher loads, run the Nonverbal behavior generator, NPC Editor, both the Speech Recognition Client and Server( you should run the server before running the client) , SBGUI and the Logger. The Logger usually runs by default from the launcher.bat file. It takes the system a few minutes to load and all of the components should be ready to go
 
#### Configuring NPC Editor
 After loading the various components. Make sure NPC editor is pointing to the robot.plist file File -> Open -> robot.plist
 
#### Loading Virtual Human and Robot Script
 Open Smartbody through the SBGUI and select File -> Load from script -> and load the AndoScript.py from the Smartbody CharacterScripts directory in the Android Project. This should load the virtual human into the current scene. You can hold Shift +Alt + right mouse click,  and move the mouse to zoom in and out and hold Shift +Alt + left mouse click,  and move the mouse to move the camera around. The Smartbody manual located in the smartbody directory has more information on how to utilize the different aspects of smartbody
 
 To connect the system to the robot, you should run the Robot Controller.py file located in the CharacterScripts directory. You can load it from smartbody: File -> Run Script -> RobotController.py. Make sure you have the correct ip address. The system currently sends commands using UDP but can be updated for TCP/IP. 
 
#### NVBG
 Make sure NVBG has Rachel selected as the current character. 


If you've executed all of these steps and your audio files and bmls are stored in the sound folder, your system should be ready to go

To test, open acquired speech, make sure the current session is started ( if the button in the upper right hand corner says stop session, then the session is currently running, if not, clikc the start session button to begin), and push and hold the gray button to speak. once you are done speaking, release the button and the system should recognized your input. below the button, you should see your current input.

#### Creating Audio Files 
To generate the audio files which serves as the robot's voice, you can either use prerecorded audio, or generate them using ttsrelay and the TexttoAudioFile.py located in the repository). If you use prerecorded audio, make sure to save your audio file in the smartbody/data/sounds founder with a text file of the same name. The text file should contain the text of the  utterance of the audio file.For example, if my audio files says "Hello, my name is bob" and the name of the file is hello.wav, then the corresponding text file should be hello.txt and the text in that file should be "Hello, my name is bob" you can look at the current set up on the SENRYAKU machine for help. 

To generate the Audio files using the TexttoAudioFile.py Updated the utterance.txt file with the utterance you want,  and the name of the outputted file. Each line you input will generate an individual audio clip, and should look as follows
```
utterance [tab] filename
```
you should input the utterance and file name without any attention. They should be seperated by a tab

The TexttoAudioFile.py automatically stores the generated audio files in the smartbody/data/sounds directory. The only edits you might need to make is to make sure line 35 of the TexttoAudioFile points to your smartbody sounds folder. 

#### Generating BMLs from Audio Files
Once you've created all of the audio files you need, run the createbml.bat file. Make sure to update the sounds file path in createbml.bat(line 5)  to point to the appropriate smartbody/data/sounds directory. The script goes through the sounds directory and generates bml for all the audio file and text file combinations. You do not have to do anything else. 

#### Generating Language model
If you've made substantial edits to the dialogue, you may want to update the language model: 
By  generating a new language model for pocket sphinx,  it allows the system to more easily recognize the words you want. To generate a new language model, you simply go to C:\vhtoolkit\data\pocketsphinx and updated the corpus.txt file with the new utterances the human is likely to say. you can remove all of the text currently in this file or you can simply add your new utterances at the button. Once you've done that, run the generate_language_model.bat script. It is located in the data\pocketsphinx director

### Adding new lines of dialogue
 build dialog system using npc editor by inputting user's question and system's responses and linking the two( I have provided a video on how to do so and a sample robot.plist file. For more information on how to do this, please visit the links provided below.   
		1. instructions for adding new dialog or changing the plist files can be found at the provided url. There is also a robot.plist file which you can load into npc editor and use: [adding new dialogue](https://confluence.ict.usc.edu/display/VHTK/NPCEditor) and here 
		2. here is a link to how you can quickly add new lines: [adding new line](https://confluence.ict.usc.edu/display/VHTK/Adding+a+New+Line+of+Dialogue+with+the+NPCEditor)



 

