""" Creates a preview animation that is cleaned up appropriately.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import FxStudio
import config
import commands
from fbximporterror import FBXImportError


class PreviewAnimation(object):
    """ Creates and maintains a dummy preview animation over the lifetime of
    the object.

    Remembers the state of the animation selection in FaceFX Studio when the
    object is entered and resets it on exit.

    """
    def __init__(self, animation_name):
        self.animation_name = animation_name
        self.created_group = False
        self.created_anim = False

    def __enter__(self):
        self.cached_group_name = FxStudio.getSelectedAnimGroupName()
        self.cached_anim_name = FxStudio.getSelectedAnimName()

        try:
            commands.create_anim_group(config.PREVIEW_GROUP_NAME)
            self.created_group = True

            commands.create_anim(
                config.PREVIEW_GROUP_NAME,
                config.PREVIEW_ANIM_NAME)
            self.created_anim = True

            commands.select_animation(
                config.PREVIEW_GROUP_NAME,
                config.PREVIEW_ANIM_NAME)

            commands.set_preview_anim(self.animation_name)
        except FBXImportError:
            self.cleanup()
            raise

        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def cleanup(self):
        if self.created_anim:
            commands.remove_anim(
                config.PREVIEW_GROUP_NAME,
                config.PREVIEW_ANIM_NAME)

        if self.created_group:
            commands.remove_anim_group(config.PREVIEW_GROUP_NAME)

        commands.select_animation(
            self.cached_group_name,
            self.cached_anim_name)
