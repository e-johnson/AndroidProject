""" Message handlers for the FBX importer plugin.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import os
import wx

import FxStudio
import FxHelperLibrary

import FBXImporter

from pluginoptions import PluginOptions
from fbximporterror import FBXImportError
from ogrefbxproxy import OgreFBXProxy
from helper import path_has_extension, get_render_asset_name,\
    get_animation_name_from_path
from fbxanims import FBXAnims
from ui import is_notification_dialog_visible, show_notification_dialog,\
    get_remembered_selection, show_options_dialog
import time


_forward_warnings = False

_missing_paths = {}


def start_forwarding_warnings():
    global _forward_warnings
    _forward_warnings = True


def stop_forwarding_warnings():
    global _forward_warnings
    _forward_warnings = False


def is_forwarding_warnings():
    global _forward_warnings
    return _forward_warnings


def on_message_logged(log_type, message):
    """Forwards warning log messages to the Python output window. """
    if _forward_warnings:
        if log_type == 'Warning':
            print message


def on_drop(files):
    """Handles files dropped on the viewport. """
    try:
        # If there is not an .fbx file present in the file list, ignore it.
        if len([x for x in files if path_has_extension(x, '.fbx')]) == 0:
            return

        fbx_file = _get_fbx_file(files)
        betf_file = _get_betf_file(files)

        if not FxStudio.isActorLoaded():
            FBXImporter.full_import_fbx(fbx_file, betf_file)
        else:
            if len(FxStudio.getFaceGraphNodeNames()) > 0:
                msg = "Dragging an FBX file onto an empty actor will set up the "
                msg += "character for you. Dragging an fbx file onto an actor "
                msg += "with an existing face graph will update the render asset. "
                msg += "No auto updating will occur.  Do you want to continue?"
                if FxStudio.displayYesNoBox(msg) == "yes":
                    FBXImporter.render_asset_only_import(fbx_file)
            else:
                FBXImporter.full_import_fbx(fbx_file, betf_file)

    except FBXImportError as e:
        FxStudio.warn(': '.join(['FBXImporter', str(e)]))


def on_renderassetloadfailed():
    """Called when a render asset load failed."""
    current_time = time.time()
    options = PluginOptions()
    # Reset the file modification time of the Base FBX to trigger an import.
    if options.fbx_abs_path:
        options.fbx_modification_timestamp = current_time


def on_idle():
    """Called when Studio is idle. Check for updates to monitored files. """
    if not FxStudio.isActorLoaded():
        return

    # If the notification dialog is currently visible return immediately.
    if is_notification_dialog_visible():
        return

    try:
        options = PluginOptions()
        fbx_path = options.fbx_abs_path

        if fbx_path:
            if not os.path.exists(fbx_path):
                if _update_from_relative_paths():
                    # update the FBX path from the new options.
                    fbx_path = options.fbx_abs_path
            if not os.path.exists(fbx_path):
                if not fbx_path in _missing_paths:
                    _missing_paths[fbx_path] = fbx_path
                    FxStudio.warn('Linked FBX file not found: {0}'.format(fbx_path))
                return
            fbx_anims = FBXAnims(fbx_path)
            #print 'disk', fbx_anims.disk_animations
            #print 'cached', fbx_anims.cached_animations
            #print 'added', fbx_anims.added_animations
            #print 'removed', fbx_anims.removed_animations
            #print 'changed', fbx_anims.changed_animations

            if _is_anything_modified(options, fbx_anims):
                import_render_asset = False
                update_render_asset = False

                selection = wx.ID_YES

                remembered_selection = get_remembered_selection()

                if remembered_selection is not None:
                    selection = remembered_selection
                else:
                    selection = show_notification_dialog()

                if selection == wx.ID_NO:
                    # Update the timestamps on anything that changed to prevent
                    # this notification from popping up again... also run the
                    # render asset update but NOT the actor update.

                    # This has the side effect of updating the base fbx file
                    # timestamp.
                    _is_base_fbx_modified(options)

                    # This has the side effect of updating the batch export
                    # text file timestamp.
                    _is_betf_modified(options)

                    # Remove all animations from the render asset that have been
                    # removed from the local disk.
                    for path in fbx_anims.removed_animations:
                        FBXImporter.remove_animation(fbx_path, path)
                        update_render_asset = True

                    # If the pose animation was removed, import the render asset
                    # so that the system will know the poses should come from the
                    # base fbx file instead.
                    if fbx_anims.is_pose_anim_removed():
                        import_render_asset = True
                        update_render_asset = True

                    if import_render_asset:
                        with FxHelperLibrary.Progress("Synchronizing...") as progress:
                            progress.update(0.05)
                            # If a pose animation exists, the poses will come from the
                            # external animation. Otherwise, the poses will come from the
                            # base fbx.
                            poses_are_in_base_fbx = not fbx_anims.pose_anim_exists()
                            progress.update(0.1)
                            # Import the render asset. We ask the importer to only touch
                            # the internal animation if the poses will come from it.
                            FBXImporter.import_render_asset(fbx_path,
                                export_internal_animation=poses_are_in_base_fbx)
                            # We need to reimport all other animations without modifying
                            # their timestamps.
                            _reimport_animations(fbx_path, fbx_anims, progress)
                            progress.update(1.0)
                            # Poses may need to be updated as a result of this but
                            # the user specifically selected no when we asked for
                            # permission to do so.

                    if fbx_anims.is_pose_anim_modified():
                        # [Re]import the pose animation.
                        FBXImporter.import_animation(fbx_path,
                            fbx_anims.get_pose_anim_path())
                        update_render_asset = True

                    if fbx_anims.is_other_anim_modified():
                        # [Re]import all of the other animations.
                        for path in fbx_anims.get_updated_animations_ex_pose_anim():
                            FBXImporter.import_animation(fbx_path, path)
                        update_render_asset = True

                    # Update the render asset if necessary to get the changes to the
                    # base fbx or the animations shown in Studio.
                    if update_render_asset:
                        FBXImporter.update_render_asset(fbx_path)

                    return
                # wx.ID_CANCEL indicates that the user pressed the options
                # button.
                elif selection == wx.ID_CANCEL:
                    show_options_dialog(wx.CommandEvent())
                    # Don't do anything else.
                    return

                update_poses = False
                add_new_ogre_anims = False

                # Remove all animations from the render asset that have been
                # removed from the local disk. Do this first so the poses can come
                # in from the basefbx in case the user removed the pose animation.
                for path in fbx_anims.removed_animations:
                    FBXImporter.remove_animation(fbx_path, path)
                    FBXImporter.remove_ogre_anim(get_animation_name_from_path(path))
                    update_render_asset = True

                # If the pose animation was removed, import the render asset
                # so that the system will know the poses should come from the
                # base fbx file instead.
                if fbx_anims.is_pose_anim_removed():
                    import_render_asset = True
                    update_render_asset = True

                if _is_base_fbx_modified(options):
                    FxStudio.msg('{0} changed. Reimporting.'.format(fbx_path))
                    import_render_asset = True
                    update_render_asset = True

                if import_render_asset:
                    with FxHelperLibrary.Progress("Synchronizing...") as progress:
                        progress.update(0.05)
                        # If a pose animation exists, the poses will come from the
                        # external animation. Otherwise, the poses will come from the
                        # base fbx.
                        poses_are_in_base_fbx = not fbx_anims.pose_anim_exists()
                        progress.update(0.1)
                        # Import the render asset. We ask the importer to only touch
                        # the internal animation if the poses will come from it.
                        FBXImporter.import_render_asset(fbx_path,
                            export_internal_animation=poses_are_in_base_fbx)
                        # We need to reimport all other animations without modifying
                        # their timestamps.
                        _reimport_animations(fbx_path, fbx_anims, progress)
                        progress.update(1.0)
                        # Poses will need to be updated as a result of this step iff
                        # the poses came from *this* fbx.
                        if poses_are_in_base_fbx:
                            update_poses = True

                if _is_betf_modified(options):
                    FxStudio.msg('{0} changed. Reimporting.'.format(options.betf_abs_path))
                    # If the batch export text file changed, we'll need to update
                    # the poses regardless of where they came from.
                    update_poses = True

                if fbx_anims.is_pose_anim_modified():
                    # [Re]import the pose animation. There is logic internal to
                    # this process to only update our internal cache if the
                    # animation is the pose animation.
                    FBXImporter.import_animation(fbx_path,
                        fbx_anims.get_pose_anim_path())
                    # Because the pose animation changed, the poses will need to be
                    # updated.
                    update_poses = True
                    update_render_asset = True
                    add_new_ogre_anims = True

                if fbx_anims.is_other_anim_modified():
                    # [Re]import all of the other animations. No caching occurs,
                    # because it is guaranteed that none of the animations in this
                    # list are the pose animation.
                    for path in fbx_anims.get_updated_animations_ex_pose_anim():
                        FBXImporter.import_animation(fbx_path, path)
                    update_render_asset = True
                    add_new_ogre_anims = True

                # Update the render asset if necessary to get the changes to the
                # base fbx or the animations shown in Studio.
                if update_render_asset:
                    FBXImporter.update_render_asset(fbx_path)

                # At this point, we can update poses and it should take into
                # account all changes to the render asset.
                if update_poses:
                    FBXImporter.update_poses()

                if add_new_ogre_anims:
                    FBXImporter.create_ogre_anims()

    except (FBXImportError, os.error) as e:
        FxStudio.warn(': '.join(['FBXImporter', str(e)]))


# Helper functions

def _get_fbx_file(files):
    """Returns the fbx file from the list of files. Raises FBXImportError if
    zero or multiple fbx files were present.

    """
    fbx_files = [x for x in files if path_has_extension(x, '.fbx')]
    if len(fbx_files) == 1:
        return fbx_files[0]
    else:
        raise FBXImportError('Please drag one FBX at a time, please.')


def _get_betf_file(files):
    """Returns the [presumptive] betf file from the list of files. Returns None
    if zero or multiple text files were present.

    """
    txt_files = [x for x in files if path_has_extension(x, '.txt')]
    if len(txt_files) == 1:
        return txt_files[0]
    else:
        return None


def _is_base_fbx_modified(options):
    """Returns True if the FBX has been modified.
    Side effect: updates the modification time in the options.

    """
    result = False
    fbx_path = options.fbx_abs_path
    if os.path.exists(fbx_path):
        fbx_timestamp = os.path.getmtime(fbx_path)

        if fbx_timestamp != options.fbx_modification_timestamp:
            result = True

        options.fbx_modification_timestamp = fbx_timestamp

    return result


def _is_betf_modified(options):
    """Returns True if the BETF has been modified.
    Side effect: updates the modification time in the options.

    """
    result = False
    betf_path = options.betf_abs_path
    if os.path.exists(betf_path):
        betf_timestamp = os.path.getmtime(betf_path)

        if betf_timestamp != options.betf_modification_timestamp:
            result = True

        options.betf_modification_timestamp = betf_timestamp

    return result


def _is_base_fbx_modified_no_modify(options):
    """Returns True if the FBX has been modified. """
    fbx_path = options.fbx_abs_path

    if os.path.exists(fbx_path):
        fbx_timestamp = os.path.getmtime(fbx_path)

        if fbx_timestamp != options.fbx_modification_timestamp:
            return True

    return False


def _is_betf_modified_no_modify(options):
    """Returns True if the BETF has been modified. """
    betf_path = options.betf_abs_path

    if os.path.exists(betf_path):
        betf_timestamp = os.path.getmtime(betf_path)

        if betf_timestamp != options.betf_modification_timestamp:
            return True

    return False


def _is_anything_modified(options, fbx_anims):
    """Returns True if anything the plugin is tracking has been modified. """
    if _is_base_fbx_modified_no_modify(options):
        return True

    if _is_betf_modified_no_modify(options):
        return True

    if len(fbx_anims.removed_animations) > 0:
        return True

    if fbx_anims.is_pose_anim_modified():
        return True

    if fbx_anims.is_other_anim_modified():
        return True

    return False


def _reimport_animations(fbx_path, fbx_anims, progress):
    """Reimports all animations in fbx_anims without modifying any cache,
    timestamps, or options. """
    for anim in fbx_anims.get_all_animations():
        ogre_fbx_proxy = OgreFBXProxy()
        ogre_fbx_proxy.import_animation(anim, get_render_asset_name(fbx_path), False)
        progress.update(progress.get_percentage_complete() + 0.01)


def _update_from_relative_paths():
    """Updates the absolute paths stored in the plugin options using the
    relative paths and the current clientspec, but only if the new absolute
    paths are found. Returns true if anything was updated, false if nothing was
    updated."""
    options = PluginOptions()
    current_time = time.time()
    updated = False
    if not os.path.exists(options.fbx_abs_path) and not options.fbx_rel_path == None:
        abs_fbx_path = os.path.abspath(os.path.join(FxStudio.getDirectory(
            'clientspec_root'), options.fbx_rel_path))
        if os.path.exists(abs_fbx_path):
            FxStudio.msg("Updating absolute FBX path from relative: {0} to {1}"
                .format(options.fbx_abs_path, abs_fbx_path))
            options.fbx_abs_path = abs_fbx_path
            options.fbx_modification_timestamp = current_time
            updated = True

    if not os.path.exists(options.betf_abs_path) and not options.betf_rel_path == None:
        abs_betf_path = os.path.abspath(os.path.join(FxStudio.getDirectory(
            'clientspec_root'), options.betf_rel_path))
        if os.path.exists(abs_betf_path):
            FxStudio.msg("Updating absolute BETF path from relative: {0} to {1}"
                .format(options.betf_abs_path, abs_betf_path))
            options.betf_abs_path = abs_betf_path
            options.betf_modification_timestamp = current_time
            updated = True
    return updated
