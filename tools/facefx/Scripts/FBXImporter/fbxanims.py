""" Helper class to manage the FBX animations for a given base FBX.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import os

from helper import find_anim_fbxs_for, is_pose_anim
from pluginoptions import PluginOptions


class FBXAnims:
    """Utilities for working with the set of animations for a given fbx. """

    def __init__(self, fbx_path):
        plugin_options = PluginOptions()
        self.disk_animations = set(find_anim_fbxs_for(fbx_path))
        self.cached_animations = plugin_options.get_fbx_anims_as_set()

        # the added and removed animations are the set differences.
        self.added_animations = self.disk_animations - self.cached_animations
        self.removed_animations = self.cached_animations - self.disk_animations

        # static animations (those that are both on disk and in our cache)
        # are the intersection of the two sets.
        self.static_animations = self.disk_animations & self.cached_animations

        # static animations can change if their modification time is more
        # recent than what we have cached.
        self.changed_animations = set([x for x in self.static_animations if
            os.path.getmtime(x) != plugin_options.get_fbx_anim_timestamp(x)])

        # the set of updated animations is the union of those that were
        # added and those that were changed.
        self.added_or_changed_animations = self.added_animations | self.changed_animations

    def pose_anim_exists(self):
        """Returns True if the pose animation exists on disk. """
        return any([is_pose_anim(x) for x in self.disk_animations])

    def is_pose_anim_modified(self):
        """Returns True if the pose animation has been modified. """
        return any([is_pose_anim(x) for x in self.added_or_changed_animations])

    def is_pose_anim_removed(self):
        """Returns True if the pose animation has been removed. """
        return any([is_pose_anim(x) for x in self.removed_animations])

    def get_pose_anim_path(self):
        """Returns the path to the pose animation. """
        for path in self.disk_animations:
            if is_pose_anim(path):
                return path
        return None

    def is_other_anim_modified(self):
        return len(self.get_updated_animations_ex_pose_anim()) > 0

    def get_all_animations(self):
        return self.static_animations

    def get_updated_animations_ex_pose_anim(self):
        """Returns a list of the updated animations, excluding the pose
        animation.

        """
        return set([x for x in self.added_or_changed_animations if not is_pose_anim(x)])

    def get_removed_animations_ex_pose_anim(self):
        """Returns a list of the removed animations, excluding the pose
        animation.

        """
        return set([x for x in self.removed_animations if not not is_pose_anim(x)])
