# AndroidProject 
This Read me File provides instructions on how to downloand and install the components of the Android version of the VhTool kit and how to run the system


## Installing the system 
The first step in getting the system runnning is to install the virtual human toolkit and it's 3rd party dependencies, and smartbody.
The toolkit comes with a version of smartbody, but it's currently an older version which is imcompatible with the current system set up 
[Download Installer Here:] (https://www.dropbox.com/sh/kwj3j6y6j8b0s4z/AADdTkipPNo22SrxKRqxfDd6a?dl=0)

By default, smartbody should be downloaded in your Document directory and the vhtoolkit is dowloaded in the C:\ directory. 

Once you have smartbody and the vhtoolkit installed, open the run-toolkit-sbgui-monitor.bat file  
 ```
 C:\vhtoolkit\bin\launcher-scripts\run-toolkit-sbgui-monitor.bat
 ```
 and change the first line to point to the bin folder of your Smartbody install. On the current machine Smartbody is located in the documents folder and that lines looks like this 
 ```
 @pushd C:\Users\SENRYAKU\Documents\SmartBody\bin
 ```
 Also, make sure to add the robot.plist file to calssifier folder:
 ```
 C:\vhtoolkit\data\classifier
 ```
 
 Create a directory called sounds in the data directory of Smartbody. This is were you will load your audio files and bml files will be stored. 
From these steps, your system should be able to launch and run without a problem. 
 
 
##Running the full System. 
 To run the system, you can execute the run-launcher.bat file. located in the AndroidProject folder. There is also a version in the vhtoolkit directory which works just as fine. 
 Once the launcher loads, run the Nonverbal behavior generator, npceditor, both the Speech Recognition Client and Server( you should run the server before running the client) , SBGUI and the Logger. The Logger usually runs by default when you execute the launcher.bat file. Make the system a few minutes to load and all of the components should be ready to go
 
#### Configuring NPC Editor
 After loading the various components. Make sure NPC editor is pointing to the robot.plist file by opening NPC editor, then selected File -> Open -> robot.plist
 
#### loading virtual human and robot script
 Open Smartbody through the SBGUI and select File -> Load from script -> and load the AndoScript.py from the Smartbody CharacterScripts directory in the Android Project. This should load the virtual human into the current scene. You can hold Shift +Alt + right mouse click and move the mouse to zoom in and out and hold Shift +Alt + left mouse click and move the mouse to move the camera around. 
 
 To connect the system to the robot, you should run the Robot Controller.py file located in the CharacterScripts directory. You can load it from smartbody: File -> Run Script -> RobotController.py
 
#### NVBG
 Make sure NVBG has Rachel selected as the current character. 

If you've executed all of these steps and your audio files and bmls are stored in the sound folder, you system should be ready to go

To test, open acquired speech, click the start session button in the upper right hand corner, and push and hold the gray button to speak. once you are done, you can release the button and the system should recognized your input. below the button, you should see your current input.

#### Creating Audio Files 
To generate the audio files which serves as the robot's voice, you can either use prerecorded audio or you can generate them using ttsrelay and the TexttoAudioFile.py located in the repository). If you use prerecorded audio, make sure to save that file in the smartbody/data/sounds founder with a text file of the same name. The text file should have the actually utterance of the audio file. you can look at the current set up on the SENRYAKU machine for help. 

To generate the Audio files using the TexttoAudioFile.py, you can change the voice of the robot by editing line 19  The listofvoice.txt file has a list of all of the available voices you can choose from. You will also see a list of voices if you run ttsrelay from the launcher ( show image of tts relay). Updaed the utterance.txt file with the utterance you want and the name of the file. Each line should look as follows
```
utterance [tab] filename
```
you should input the  utterance and file name without any attention. They should be seperated by a tab

It automatically stores those files in the smartbody/data/sounds directory. The only edits you might need to make is to make sure line 35 points to your smartbody sounds folder. 

#### Generating BMLs from Audio Files
Once you've created all of the audio files you need, run the createbml.bat file. Make sure to update the sounds file path in createbml.bat(line 5)  to point to the appropriate ones. The script goes through the sounds directory and generates bml for all the audio file and text file combinations. You do not have to do anything else. 

#### Generating Language model
Once youve made substantial edits to the dialogue, you want to make sure to update the language model: 
By  generating a new language model for pocket sphinx,  it allows the system to more easily recognize the words you want. To generate a new language model, you simply go to C:\vhtoolkit\data\pocketsphinx and updated the corpus.txt file with your new utterances the human is likely to say. you can remove all of the text currently in this file or you can simply add your new utterances at the button. Once you've done that, run the generate_language_model.bat script located in that same folder

### Adding new lines of dialogue
 build dialog system using npc editor by inputting user's question and system's responses and linking the two( I have provided a video on how to do so and a sample robot.plist file. For more information on how to do this, please visit the links provided below.   
		1. instructions for adding new dialog or changing the plist files can be found at the provided url. There is also a robot.plist file which you can load into npc editor and use: [adding new dialogue](https://confluence.ict.usc.edu/display/VHTK/NPCEditor) and here 
		2. here is a link to how you can quickly add new lines: [adding new line](https://confluence.ict.usc.edu/display/VHTK/Adding+a+New+Line+of+Dialogue+with+the+NPCEditor)



 

