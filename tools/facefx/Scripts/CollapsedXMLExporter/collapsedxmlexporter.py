""" CollapsedXMLExporter FaceFX Studio Plugin implementation.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.
"""

import os
import re
import tempfile

import wx
import FxStudio

from FxHelperLibrary import Unattended, Progress


MENU_EXPORT_ID = wx.NewId()


def _export_collapsed_xml(actor_path, xml_file):
    """ Exports collapsed XML file.

    """
    with Unattended():
        with Progress("Collapsing Actor...") as progress:

            progress.update(.05)

            collapsed_actor = tempfile.gettempdir() + '\\' + os.path.basename(re.sub('\.facefx', '-FG_Collapsed.facefx', actor_path))

            bone_pose_names = get_bone_pose_nodes();

            # Export a collapsed version of the file.
            FxStudio.issueCommand('fgcollapse -file "{0}" -output "{1}" -fn "{2}"'.format(actor_path, collapsed_actor, bone_pose_names))

            progress.update(1)

            if not os.path.exists(collapsed_actor):
                message = 'Could not load collapsed actor! Make sure you have '
                message += 'write permsission to the directory: "{0}"'.format(os.path.dirname(collapsed_actor))
                raise FxStudio.FaceFXError(message)

            # Load the collapsed actor.
            FxStudio.issueCommand('loadActor -file "{0}"'.format(collapsed_actor))

            FxStudio.issueCommand('actorxml -file "{0}"'.format(xml_file))

            # Load the original actor back up.
            FxStudio.issueCommand('loadActor -file "{0}"'.format(actor_path))

            # Delete the temporary collapsed actor file.
            os.remove(collapsed_actor)

def get_bone_pose_nodes():
    """ Returns a string with all bone pose node names in the actor separated by '|'

    """
    bone_pose_names = ""
    for node in FxStudio.getFaceGraphNodeNames():
        if FxStudio.getFaceGraphNodeProperties(node)[0] == 'FxBonePoseNode':
            bone_pose_names = bone_pose_names + node + '|'
    return bone_pose_names

def on_menu_export(event_id):
    """ Called when the user selects the menu option to export collapsed xml.

    """
    if FxStudio.isNoSave():
        FxStudio.error('This operation is disabled in no-save.')
    else:
        if FxStudio.containsUnsavedChanges():
            FxStudio.error('Please save the actor before continuing.')
        else:
            actor_path = FxStudio.getActorPath()
            if len(actor_path) > 0:
                initial_xml_path = re.sub('\.facefx', '.xml', actor_path)
                xml_file = FxStudio.displayFileSaveDialog(msg='Export FaceFX Actor to XML',\
                    default_path=os.path.dirname(initial_xml_path),\
                    default_filename=os.path.basename(initial_xml_path),\
                    wildcard='Actor XML Files (*.xml)|*.xml',\
                    confirm_overwrite=True)
                if xml_file is not None:
                    _export_collapsed_xml(actor_path, xml_file)
            else:
                FxStudio.error('Please save the actor before continuing.')
