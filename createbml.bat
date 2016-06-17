pushd tools\facefx
call facefx-studio -exec "..\VisemeSchedulerFacefx\example_batch.fxl"


pushd C:\Users\SENRYAKU\Documents\SmartBody\data\sounds
call VisemeSchedulerFacefxd.exe robot.xml
pushd ../..
call python changefileextentions.py
@popd
