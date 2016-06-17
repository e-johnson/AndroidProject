# This script plays the next animation.  Useful when previewing lots of anims.

from FxStudio import *

selectedCurves = getSelectedCurves()

selectedGroup = getSelectedAnimGroupName()
selectedAnim = getSelectedAnimName()
animationNames = getAnimationNames()

animToSelect = ""
groupToSelect = ""

totalAnims = 0

for group in animationNames:
    numAnims = getNumAnimationsInGroup(group[0])
    totalAnims = totalAnims + numAnims
    if numAnims != 0:
        # This is the first animation.  Make it the default.
        animToSelect = group[1][0]
        groupToSelect = group[0]
        break

if totalAnims == 0:
    errorBox("This script require at least one animation in the actor to run.")
    raise RuntimeError("No anims in actor.")

bSelectNextAnim = 0

for group in animationNames:
    if (group[0] == selectedGroup) or (bSelectNextAnim == 1):
        if selectedAnim == "":
            # there is no selected animation, so select the next animation in the selected group.
            bSelectNextAnim = 1
        for anim in group[1]:
            if bSelectNextAnim == 1:
                # This is the first animation after the selected anim.
                animToSelect = anim
                groupToSelect = group[0]
                bSelectNextAnim = 2
                break
            if (anim == selectedAnim):
                #this is the sselected anim.
                bSelectNextAnim = 1
    if bSelectNextAnim == 2:
        break
selectAnimation(groupToSelect, animToSelect)

curveSelect = ""
for curve in selectedCurves:
    curveSelect += curve + "|"
issueCommand('select -type "curve" -names "%s";' % (curveSelect))

issueCommand("play")
