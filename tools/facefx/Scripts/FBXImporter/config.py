""" Configuration settings for the FBX importer plugin.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import FxStudio


# Path to the OgreFBX converter
OGREFBX_PATH = ''.join([FxStudio.getDirectory('app'), 'ExecFxOgreFBX.exe'])

OGREFBX_LOG_PATH = FxStudio.getLogFileFullPath('fbximporter-log.txt')
USE_FBX_START_TIME = '-100000'
USE_FBX_END_TIME = '100000'

# Path to the mesh export location.
FBX_IMPORTER_CACHE_DIR = ''.join([FxStudio.getDirectory('user'),
    'Ogre\\Resources\\FBXImporterCache\\'])

DEFAULT_TEMPLATE_PATH = ''.join([FxStudio.getDirectory('app'),
    'Samples\\Src\\DefaultTemplate.fxt'])
DEFAULT_BATCH_EXPORT_PATH = ''.join([FxStudio.getDirectory('app'),
    'Samples\\Src\\Batch-Export.txt'])

FBX_PLUGIN_DICTIONARY_KEY = 'fbximporter'

FBX_ANIMATION_GROUP = 'FBX@Animations'

# The last path browsed to by the user for the fbx file.
FBX_ABS_PATH_KEY = 'fbx_absolute_path'
FBX_REL_PATH_KEY = 'fbx_relative_path'
FBX_MODIFIED_TIMESTAMP = 'fbx_timestamp'
# The last path browsed to by the user for the batch export text file
BETF_ABS_PATH_KEY = 'betf_absolute_path'
BETF_REL_PATH_KEY = 'betf_relative_path'
BETF_MODIFIED_TIMESTAMP = 'betf_timestamp'

# The fbx animation dictionary
ANIM_DICTIONARY_KEY = 'fbx_anim_dict'
# The last-seen framerate
FRAMERATE_KEY = 'fbx_anim_framerate'
# The last-seen keyframes
KEYFRAMES_KEY = 'fbx_anim_keyframes'

# The animation where we can expect to find bone poses.
PREVIEW_GROUP_NAME = '_fbx_import'
PREVIEW_ANIM_NAME = '_fbx_import_bone_poses_'
# Note the _facefx_ prefix causes this animation to be hidden from
# the user interface -- don't change this prefix here.
FRAME_ZERO_ANIM_NAME = '_facefx_rest_anim_'

# The special animation name that we can expect to find our poses in.
POSE_ANIM_NAME = 'facefx_poses'

# Nodes to automatically rig if we find positive and negative versions.
POSITIVE_SUFFIX = '_Pos'
NEGATIVE_SUFFIX = '_Neg'
AUTO_RIG_NODES = {'Head_Pitch': 'Head Pitch', 'Head_Yaw': 'Head Yaw',
    'Head_Roll': 'Head Roll', 'Eyes_Pitch': 'Eye Pitch', 'Eyes_Yaw': 'Eye Yaw'}
