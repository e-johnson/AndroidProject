# This script plays the previous animation.  Useful when previewing lots of anims.

from FxStudio import *
selectedCurves = getSelectedCurves()
selectedGroup = getSelectedAnimGroupName()
selectedAnim = getSelectedAnimName()
animationNames = getAnimationNames()

animToSelect = ""
groupToSelect = ""

totalAnims = 0
numGroups = getNumAnimationGroups()
i = numGroups
while i > 0:
    i -= 1
    group = animationNames[i]
    numAnims = getNumAnimationsInGroup(group[0])
    totalAnims = totalAnims + numAnims
    if numAnims != 0:
        # This is the last animation.  Make it the default.
        animToSelect = group[1][numAnims - 1]
        groupToSelect = group[0]
        break

if totalAnims == 0:
    errorBox("This script require at least one animation in the actor to run.")
    raise RuntimeError("No anims in actor.")
bSelectNextAnim = 0
i = numGroups
while i > 0:
    i -= 1
    group = animationNames[i]
    if (group[0] == selectedGroup) or (bSelectNextAnim == 1):
        if selectedAnim == "":
            # there is no selected animation, so select the prior animation in the selected group.
            bSelectNextAnim = 1
        numAnims = getNumAnimationsInGroup(group[0])
        j = numAnims
        while j > 0:
            j -= 1
            anim = group[1][j]
            if bSelectNextAnim == 1:
                # This is the first animation after the selected anim.
                animToSelect = anim
                groupToSelect = group[0]
                bSelectNextAnim = 2
                break
            if anim == selectedAnim:
                #this is thge s
                bSelectNextAnim = 1
    if bSelectNextAnim == 2:
        break
selectAnimation(groupToSelect, animToSelect)

curveSelect = ""
for curve in selectedCurves:
    curveSelect += curve + "|"
issueCommand('select -type "curve" -names "%s";' % (curveSelect))

issueCommand("play")
