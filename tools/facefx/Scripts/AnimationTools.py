#-------------------------------------------------------------------------------
# Some handy tools for editing animations in FaceFX Studio.
# Owner: Jamie Redmond
#
# Copyright (c) 2002-2012 OC3 Entertainment, Inc.
#-------------------------------------------------------------------------------

from FxStudio import *
from FxAnimation import *
from numpy import rint


# Always returns zero for ease of use in modifySelectedCurveSegmentSlopes().
def zeroSlope(curve, firstKey, secondKey):
    return 0.0


# Computes what outgoing slope on firstKey and incomingSlope on secondKey should be used
# to create a linear interpolation between firstKey and secondKey. This just computes rise / run
# for use in modifySelectedCurveSegmentSlopes().
def linearSlope(curve, firstKey, secondKey):
    return (curve.keys[secondKey].value - curve.keys[firstKey].value) / (curve.keys[secondKey].time - curve.keys[firstKey].time)


# Modifies the slopes of the selected curve segments. The computeSlope argument is the function
# to use to compute the slopes.
def modifySelectedCurveSegmentSlopes(computeSlope):
    selectedAnimInfo = getSelectedAnimation()
    selectedAnim = Animation(selectedAnimInfo[0], selectedAnimInfo[1])
    selectedCurves = getSelectedCurves()
    unlockSelectedKeyTangents()
    totalSelectedKeys = 0
    for curve in selectedCurves:
        totalSelectedKeys = totalSelectedKeys + len(getSelectedKeys(curve))
    if totalSelectedKeys > 0:
        beginProgressDisplay("Working...")
    currentKey = 1
    issueCommand("batch;")
    for curve in selectedCurves:
        selectedCurve = selectedAnim.findCurve(curve)
        selectedKeys = getSelectedKeys(curve)
        numSelectedKeys = len(selectedKeys)
        numKeysInCurve = len(selectedCurve.keys)
        if numKeysInCurve > 1:
            if numSelectedKeys == 1:
                issueCommand('warn -message "Unable to modify selected segments of curve \""%s"\" because there is only one key selected";' % (curve))
            elif numSelectedKeys > 1:
                canContinue = True
                lastIndex = selectedKeys[0]
                for i in range(1, numSelectedKeys):
                    if selectedKeys[i] != lastIndex + 1:
                        issueCommand('warn -message "Unable to modify selected segments of curve \""%s"\" because there are gaps in the selected key sequence";' % (curve))
                        canContinue = False
                        break
                    lastIndex = selectedKeys[i]
                if canContinue:
                    firstKey = 0
                    lastKey = numSelectedKeys - 1
                    lastComputedSlope = 0.0
                    for i in range(numSelectedKeys):
                        if i == firstKey:
                                lastComputedSlope = computeSlope(selectedCurve, selectedKeys[i], selectedKeys[i + 1])
                                issueCommand('key -edit -curveName "%s" -keyIndex "%d" -slopeOut "%f";' % (curve, selectedKeys[i], lastComputedSlope))
                        elif i == lastKey:
                                issueCommand('key -edit -curveName "%s" -keyIndex "%d" -slopeIn "%f";' % (curve, selectedKeys[i], lastComputedSlope))
                        else:
                            incoming = lastComputedSlope
                            lastComputedSlope = computeSlope(selectedCurve, selectedKeys[i], selectedKeys[i + 1])
                            issueCommand('key -edit -curveName "%s" -keyIndex "%d" -slopeIn "%f" -slopeOut "%f";' % (curve, selectedKeys[i], incoming, lastComputedSlope))
                        progress = float(currentKey) / float(totalSelectedKeys)
                        issueCommand('set -n "pp_overall_progress" -v "%s";' % (progress))
                        currentKey = currentKey + 1
        else:
            if numSelectedKeys == 1:
                issueCommand('warn -message "Unable to modify selected segments of curve \""%s"\" because the curve only contains one key";' % (curve))
    issueCommand("execBatch -editedcurves;")
    if totalSelectedKeys > 0:
        endProgressDisplay()


# Snaps all keys in the selected curves not owned by analysis to frames at the animation's frame rate.
def snapKeysToFrames():
    group = getSelectedAnimGroupName()
    anim = getSelectedAnimName()

    issueCommand('batch')

    if group != '' and anim != '':
        a = Animation(group, anim)
        fps = a.frameRate
        selected_curves = getSelectedCurves()
        for s in selected_curves:
            for c in a.curves:
                if c.name == s and not isCurveOwnedByAnalysis(group, anim, s):
                    for i in range(c.getNumKeys()):
                        k = c.keys[i]
                        issueCommand('key -edit -curveName "{0}" -keyIndex {1} -time {2} -value {3} -slopeIn {4} -slopeOut {5}'.format(c.name, i, rint(k.time * fps) / fps, k.value, k.slopeIn, k.slopeOut))

    issueCommand('execBatch -editedcurves')
