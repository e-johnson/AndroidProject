""" Helper functions for the FBX Importer

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import os
import re
import hashlib
import FxStudio
import config
import messagehandler
from fbximporterror import FBXImportError


def path_has_extension(path, ext):
    """Returns True when path has the given extension """
    return os.path.splitext(path)[1].lower() == ext


def make_relative_to_clientspec_root(path):
    """Makes a path relative to the clientspec root. Passes Null unaffected.

    """
    if path:
        if os.path.splitdrive(path)[0] == os.path.splitdrive(FxStudio.getDirectory('clientspec_root'))[0]:
            return os.path.relpath(path, FxStudio.getDirectory('clientspec_root'))
        else:
            return path
    return None

def get_render_asset_name(fbx_path):
    """Returns the render asset name for the fbx file. """
    # Make sure we use a relative path, so render asset names don't change with
    # source control.
    if os.path.isabs(fbx_path):
        rel_path = make_relative_to_clientspec_root(fbx_path)
    else:
        rel_path = fbx_path
    return hashlib.md5(rel_path).hexdigest()

def find_anim_fbxs_for(fbx_path):
    """Find files matching the pattern basefbx@animname.fbx in the same
    directory as the fbx in fbx_path, and return a list of the fully-qualified
    paths to the files matching the pattern.

    """
    fbx_dir, fbx_filename = os.path.split(fbx_path)
    root, extension = os.path.splitext(fbx_filename)
    animation_matcher = re.compile(root + '@(.*)\.fbx$', re.IGNORECASE)

    fbx_anims = []
    for f in os.listdir(fbx_dir):
        # Check if the file is an animation for the root fbx.
        match = animation_matcher.match(f)
        if match:
            # Construct the full path to the animation fbx.
            anim_path = os.path.join(fbx_dir, f)
            fbx_anims.append(anim_path)

    #print fbx_anims
    return fbx_anims


def is_pose_anim(fbx_anim_path):
    """Returns True if the fbx anim path point to the pose animation. """
    return '@' + config.POSE_ANIM_NAME + '.fbx' in fbx_anim_path.lower()


def get_animation_name_from_path(fbx_anim_path):
    """Returns the animation name given a full path to an fbx animation file
    named base@anim.fbx

    """
    pattern = re.compile(r'.*@(.*)\.fbx', re.IGNORECASE)
    match = pattern.search(fbx_anim_path)
    if match:
        return match.group(1)
    else:
        raise FBXImportError('Malformed fbx animation path!')


class CommandBatcher(object):
    """ Ensure that batches are closed out correctly. """
    def __init__(self, flags):
        self.flags = flags

    def __enter__(self):
        FxStudio.issueCommand('batch')
        return self

    def __exit__(self, type, value, traceback):
        FxStudio.issueCommand('execBatch {0}'.format(self.flags))
        return True


class WarningForwarder(object):
    """ Ensures that the warning forwarding system behaves correctly. """
    def __enter__(self):
        messagehandler.start_forwarding_warnings()

    def __exit__(self, type, value, traceback):
        messagehandler.stop_forwarding_warnings()
        return True
