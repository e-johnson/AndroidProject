
VisemeSchedulerFacefx instructions.


These instructions explain how to go from a FaceFX Studio .facefx file to a set of Smartbody .bml lip-sync timing files.

This is described in 2 major steps:
  - take the .facefx file, load it into FaceFX Studio, analyze a folder full of audio files, export the info to a FaceFX .xml file.
  - take the FaceFX .xml file and create a set of Smartbody .bml lip-sync timing files, one per audio file.


Step 1:

To complete this step, you will need:
  - .facefx file
     it is assumed we have a .facefx file that contains the default FaceFX phoneme to viseme set mapping.  No animations should be loaded into it.
  - audio files w/transcribed text files
     One .txt file per audio file, stored alongside
  - .fxl file
     Take the example_batch.fxl file and suit it to your needs.  It identifies the .facefx file, the folder containing the audio files, and the output filename for the resulting .xml file

Once these steps are set up, run FaceFX studio in batch mode:  (note no extension on facefx-studio executable)
..\..\tools\facefx\facefx-studio -exec ".\example_batch.fxl"


Step 2:

To complete this step, you will need:
  - .xml file from Step 1

Run the VisemeSchedulerFacefx tool:
VisemeSchedulerFacefx.exe example.xml

This will create a set of Smartbody .bml files to use with your audio files.

