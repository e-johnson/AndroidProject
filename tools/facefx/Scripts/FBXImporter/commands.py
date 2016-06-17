""" Wraps FaceFX Studio commands.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import FxStudio
from fbximporterror import FBXImportError


def clear_face_graph():
    issue_raw('graph -clear')


def layout_face_graph():
    issue_raw('graph -layout')


def create_anim_group(group_name):
    issue_raw('animGroup -create -group "{0}"'.format(group_name))


def create_anim(group_name, anim_name):
    issue_raw('anim -add -group "{0}" -name "{1}"'.format(group_name,
        anim_name))


def set_preview_anim(preview_anim_name):
    # Make absolutely sure the preview animation has zero blend times in case
    # the default ever changes in Studio.
    issue_raw(
        'previewanim -animation "{0}" -blendintime "{1}" -blendouttime "{1}"'\
        .format(preview_anim_name, 0.0))


def remove_anim(group_name, anim_name):
    issue_raw('anim -remove -group "{0}" -name "{1}"'.format(group_name,
        anim_name))


def remove_anim_group(group_name):
    issue_raw('animGroup -remove -group "{0}"'.format(group_name))


def select_animation(group_name, anim_name):
    """Selects an animation in FaceFX Studio. """
    issue_raw('select -type "animgroup" -names "{0}"'.format(group_name))
    if len(anim_name):  # it's possible to have no animation selected.
        issue_raw('select -type "anim" -names "{0}"'.format(anim_name))


def set_rest_pose():
    """Sets the rest pose. """
    issue_raw('bonepose -restpose -replacewithcurrentframe')


def prune_rest_pose():
    """Prunes the rest pose. """
    issue_raw('bonepose -prunerestpose')


def export_frame(pose_name):
    """Exports the current frame and names it pose_name. """
    issue_raw('exportframe -name "{0}"'.format(pose_name))


def set_all_boneweights_to(value):
    """Sets all the bone weights to a value. """
    issue_raw('boneweight -all -weight {0}'.format(value))


def create_combiner(name, node_min=None, node_max=None):
    """Creates a combiner node with the given min and max. """
    issue_raw('graph -addnode -nodetype "FxCombinerNode"'
        ' -name "{0}" -min {1} -max {2}'.format(name,
            node_min if node_min else 0.0,
            node_max if node_max else 1.0))


def link_linear(from_node, to_node, m=None, b=None):
    """Links two nodes together with the given link functions. """
    param_string = '-linkfnparams "m={0}|b={1}"'.format(
        m if m else 1.0, b if b else 0.0)
    issue_raw('graph -link -from "{0}" -to "{1}" -linkfn "linear" {2}'.format(
        from_node, to_node, param_string))


def link_corrective(from_node, to_node, factor=None):
    """Links two nodes together with the corrective link function. """
    param_string = '-linkfnparams "Correction Factor={0}"'.format(
        factor if factor else 1.0)
    issue_raw(
        'graph -link -from "{0}" -to "{1}" -linkfn "corrective" {2}'.format(
            from_node, to_node, param_string))


def sync_template(filename, flags=None):
    if not flags:
        flags = '-facegraph -preservebones -forcenodepositions'
    issue_raw(
        'template -sync {1} -file "{0}"'.format(filename, flags))


def add_ogre_animation_event(group_name, anim_name):
    issue_raw(
        'event -group "{0}" -anim "{1}" -add -eventgroup "{0}" -eventanim \
        "placeholder" -payload "game: playanim {1}" -blendunscaled "false" \
        -useparentblend "true"'.format(group_name, anim_name, group_name, anim_name))


def flush_undo_redo_buffers():
    """Flushes the undo and redo buffers. """
    issue_raw('flushundo')


def issue_raw(command):
    """Issues a command and raises an exception if the command fails. """
    if not FxStudio.issueCommand(command):
        raise FBXImportError('Command failed: {0}'.format(command))
