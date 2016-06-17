"""Handle the user-facing portions of the FBX to Ogre and FaceFX conversion
process.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import os

import FxStudio
import FxHelperLibrary

import config
import commands

from helper import make_relative_to_clientspec_root, get_render_asset_name,\
    find_anim_fbxs_for, is_pose_anim, CommandBatcher, WarningForwarder
from pluginoptions import PluginOptions
from fbximporterror import FBXImportError
from previewanimation import PreviewAnimation
from ogrefbxproxy import OgreFBXProxy
from betfparser import BatchExportTextFileParser


# -- DRIVER --


def full_import_fbx(fbx_path, batch_export_path=None):
    """Imports an FBX file from a path.

    parameters:

    fbx_path -- Fully-qualified path to an FBX file.
    batch_export_path [optional] -- If parameter is not provided, a dialog will
        be displayed asking the user to browse for the batch export text file.
        If the path is known, the dialog can be bypassed by providing the path
        as a parameter to this function. If you only wish to import a render
        asset without importing bone poses, passing the empty string as the path
        will do the trick.

    side effects:

    - If no actor is loaded in Studio, a new actor is created.
    - The render asset is changed to the imported FBX assets.
    - If a batch export text file is selected, the bone poses are loaded from
    the FBX file.

    """
    try:
        # Prerequisites
        _fail_if_no_ogrefbx()
        _ensure_exists_actor()
        _ensure_exists_importer_cache()

        if batch_export_path is None:
            batch_export_path = _get_betf_path_from_user()

        # Cache the FBX and BETF path
        options = PluginOptions()

        options.betf_abs_path = batch_export_path
        options.betf_rel_path = make_relative_to_clientspec_root(batch_export_path)

        # Set the fbx_export_input_file console variable to the fbx file.
        FxStudio.setConsoleVariable('fbx_export_input_file', fbx_path)

        with FxHelperLibrary.Progress("Importing FBX...") as progress:
            progress.update(0.05)

            # Convert the base FBX to a render asset.
            import_render_asset(fbx_path, progress)

            # Update the options.  This will enable automatic updating
            options.fbx_abs_path = fbx_path
            options.fbx_rel_path = make_relative_to_clientspec_root(fbx_path)

            # Find any animations for the base FBX and add them to the render asset.
            _find_and_create_animations_for(fbx_path)
            progress.update(0.25)

            # Set the render asset in the actor.
            update_render_asset(fbx_path)
            progress.update(0.3)

            # Create FaceFX animations for the imported Ogre body animations.
            create_ogre_anims()

            if update_poses(progress):
                rig_new_import()
                progress.update(0.97)

            with FxHelperLibrary.Unattended():
                # Sync to the default template to get the color map and workspaces.
                commands.sync_template(config.DEFAULT_TEMPLATE_PATH, flags='-workspaces -colormap')

            commands.flush_undo_redo_buffers()

            progress.update(1.0)

        # Cache the correct timestamps
        if os.path.exists(batch_export_path):
            options.betf_modification_timestamp = os.path.getmtime(batch_export_path)
        options.fbx_modification_timestamp = os.path.getmtime(fbx_path)

    except (RuntimeError, FBXImportError) as e:
        options.clear()
        commands.flush_undo_redo_buffers()
        FxStudio.warn(': '.join(['FBXImporter', str(e)]))


def render_asset_only_import(fbx_path):
    "A simple import of the FBX as the render asset, without tracking files."
    _fail_if_no_ogrefbx()
    try:
        with FxHelperLibrary.Progress("Importing FBX...") as progress:

            progress.update(0.05)

            # Convert the base FBX to a render asset.  If this fails, the
            # exception we will caught before any work is done from the calls
            # below.  The goal is to warn about the failure without changing
            # anything.
            import_render_asset(fbx_path, progress)
            progress.update(0.7)

             # Set the render asset in the actor.
            update_render_asset(fbx_path)
            progress.update(1.0)

            # set the fbx_export_input_file console variable
            FxStudio.setConsoleVariable('fbx_export_input_file', fbx_path)

            # Make sure we aren't tracking files.
            options = PluginOptions()
            options.clear()
    except (RuntimeError, FBXImportError) as e:
        FxStudio.warn(': '.join(['FBXImporter', str(e)]))


def import_render_asset(fbx_path, progress=None, export_internal_animation=None):
    """Imports just the render asset from an fbx file. """

    if export_internal_animation is None:
        export_internal_animation = True

    ogre_fbx_proxy = OgreFBXProxy()
    ogre_fbx_proxy.create_render_asset(fbx_path, export_anim=export_internal_animation)

    if progress:
        progress.update(0.2)


def update_render_asset(fbx_path):
    """Forces Studio to update from the render asset. """
    FxStudio.setRenderAssetName(get_render_asset_name(fbx_path))


def import_animation(fbx_path, fbx_anim_path):
    """Imports a single animation into the render asset. """
    #print 'import_animation(fbx_path={0}, fbx_anim_path={1}'.format(fbx_path, fbx_anim_path)
    _create_single_animation_from(fbx_anim_path, get_render_asset_name(fbx_path))


def remove_animation(fbx_path, fbx_anim_path):
    """Removes a single animation from the render asset. """
    options = PluginOptions()
    render_asset_name = get_render_asset_name(fbx_path)
    # Remove the animation.
    ogre_fbx_proxy = OgreFBXProxy()
    ogre_fbx_proxy.remove_animation(fbx_anim_path, render_asset_name)
    # Remove the animation from the cache.
    options.remove_fbx_anim(fbx_anim_path)


def update_poses(progress=None):
    """Creates or updates the poses in an actor's face graph. """
    options = PluginOptions()
    pose_names = _get_pose_names(options.betf_abs_path, options.keyframes)
    frame_rate = options.framerate
    with PreviewAnimation(config.POSE_ANIM_NAME):
        # Set the rest pose in FaceFX Studio.
        if progress:
            progress.update(0.44)
        FxStudio.setCurrentTime(0.0)
        commands.set_rest_pose()

        # Create the bone poses in FaceFX Studio.
        if len(pose_names) > 0:
            if progress:
                progress.update(0.48)
            _create_poses(pose_names, frame_rate)

    commands.flush_undo_redo_buffers()

    return pose_names is not None


def rig_new_import():
    """Runs the code necessary to rig an newly-imported character. """
    # Automatically rig portions of the face graph.
    _rig_pos_neg_nodes()

    # Lay out the graph so all the nodes aren't stacked on each other.
    commands.layout_face_graph()


# Helper Functions

def _fail_if_no_ogrefbx():
    """Fails if the FxOgreFBX tool is not in the correct location. """
    if not os.path.exists(config.OGREFBX_PATH):
        raise FBXImportError('FxOgreFBX was not found at: {0}'.format(
            config.OGREFBX_PATH))


def _ensure_exists_actor():
    """Ensure an actor is loaded in Studio. Create one if necessary. """
    try:
        FxStudio.getActorName()
    except RuntimeError:
        actor_name = FxStudio.getTextFromUser('Enter new actor name: ',
            'Create Actor', 'NewActor')
        FxStudio.createNewActor(actor_name)


def _ensure_exists_importer_cache():
    """ Make sure the FBX_IMPORTER_CACHE_DIR directory exists. """
    normalized_fbx_importer_cache_dir = os.path.normpath(config.FBX_IMPORTER_CACHE_DIR)
    if not os.path.exists(normalized_fbx_importer_cache_dir):
        os.makedirs(normalized_fbx_importer_cache_dir)


def _get_betf_path_from_user():
    """Returns the batch export path. Caches the path in the dictionary. """
    options = PluginOptions()
    betf_path = FxStudio.displayFileOpenDialog(
        'Select batch export text file (if necessary)',
        os.path.dirname(options.betf_abs_path),
        os.path.basename(options.betf_abs_path),
        '',
        'Text files (*.txt)|*.txt')

    if betf_path:
        if len(betf_path) > 0:
            return betf_path
    return ""


def _find_and_create_animations_for(fbx_path):
    """Find files matching the pattern basefbx@animname.fbx and export them
    as animations in the .SKELETON file.

    """
    render_asset_name = get_render_asset_name(fbx_path)
    fbx_anims = find_anim_fbxs_for(fbx_path)
    for fbx_anim in fbx_anims:
        _create_single_animation_from(fbx_anim, render_asset_name)


def _create_single_animation_from(fbx_anim_path, render_asset_name):
    """Creates a single animation from the fbx_anim_path. """
    #print '_create_single_animation_from(fbx_anim_path="{0}", render_asset_name="{1}")'.format(fbx_anim_path, render_asset_name)
    options = PluginOptions()
    # Import the animation.
    ogre_fbx_proxy = OgreFBXProxy()
    ogre_fbx_proxy.import_animation(fbx_anim_path, render_asset_name,
        is_pose_anim(fbx_anim_path))
    # Cache the animation path and its modification time.
    options.add_fbx_anim(fbx_anim_path, os.path.getmtime(fbx_anim_path))


def _get_pose_names(batch_export_path, keys):
    """Returns a list of tuples, [(name, frame), ...] """
    pose_names = []
    if batch_export_path:
        pose_names_temp = _parse_batch_export(batch_export_path)
        # Verify that each pose is on a keyed frame, otherwise do not export the pose.
        for name, frame in pose_names_temp:
            if frame in set(keys):
                pose_names.append([name, frame])
            else:
                print "Warning! No Key exists on frame " + str(frame) + " for pose " + name + ".  Skipping bone pose."
    else:
        pose_names = _pose_names_from_frames(keys)
    return pose_names


def _parse_batch_export(batch_export_path):
    """Parses the batch export text file, returns a list of tuples,
    (target_name, frame_number), or None if betf was invalid or
    not provided.

    """
    parser = BatchExportTextFileParser(batch_export_path)
    return parser.pose_names


def _pose_names_from_frames(keys):
    """ Provides a default name for each frame specified in the keys. """
    return [('Frame_{0}'.format(frame), int(frame)) for frame in keys]


def _create_poses(pose_names, frame_rate):
    """ Creates poses for every frame from either the batch export text file,
    or if that was not provided, for every keyed frame in the FBX. """
    with WarningForwarder():
        # Set the bone weights to zero so the skeleton will move as we tick through
        # the frames in the batch export file.
        with CommandBatcher('-addednodes -changedbones'):
            commands.set_all_boneweights_to(0.0)

            inv_frame_rate = 1.0 / frame_rate
            for pose_name, frame_number in pose_names:
                # Seek to the current time.
                FxStudio.setCurrentTime(frame_number * inv_frame_rate)
                # Place the state of the character into a pose.
                commands.export_frame(pose_name)

            # Set the bone weights back to the default of 1.
            commands.set_all_boneweights_to(1.0)

        # After the batch of commands succeeds, prune bones that did not move from
        # the rest pose.
        commands.prune_rest_pose()


def _rig_pos_neg_nodes():
    """Attemps to rig the positive and negative nodes automatically.

    """
    degrees = float(30)
    inv_degrees = 1. / float(degrees)

    face_graph = FxStudio.getFaceGraphNodeNames()
    with CommandBatcher('-addednodes'):
        for node in config.AUTO_RIG_NODES.iterkeys():
            # Actual targets driven by FaceFX Studio use spaces, not underscores.
            node_name = config.AUTO_RIG_NODES[node]
            negative_node = ''.join([node, config.NEGATIVE_SUFFIX])
            positive_node = ''.join([node, config.POSITIVE_SUFFIX])
            if negative_node in face_graph and positive_node in face_graph:
                commands.create_combiner(node_name,
                    node_min=-degrees, node_max=degrees)
                commands.link_linear(node_name, negative_node, m=-inv_degrees)
                commands.link_linear(node_name, positive_node, m=inv_degrees)


def remove_ogre_anim(anim_name):
    if FxHelperLibrary.anim_exists(config.FBX_ANIMATION_GROUP + "/" + anim_name):
        commands.remove_anim(config.FBX_ANIMATION_GROUP, anim_name)


def create_ogre_anims():
    """Creates a FaceFX animation for a corresponding Ogre animation that
    be added to other anims as an event.

    """
    cached_anim = FxHelperLibrary.get_selected_animpath()
    for anim in FxStudio.getRenderAssetAnimationInfo():
        if not FxHelperLibrary.group_exists(config.FBX_ANIMATION_GROUP):
            commands.create_anim_group(config.FBX_ANIMATION_GROUP)
        if not FxHelperLibrary.anim_exists(config.FBX_ANIMATION_GROUP + "/" + anim[0]):
            commands.create_anim(config.FBX_ANIMATION_GROUP, anim[0])
            commands.issue_raw('curve -gr "{0}" -an "{1}" -a -n dampen'.format(config.FBX_ANIMATION_GROUP, anim[0]))
            commands.issue_raw('key -i -t 0 -v 1 -cn dampen')
            commands.issue_raw('key -i -t "{0}" -v 1 -cn dampen'.format(anim[1]))
            commands.add_ogre_animation_event(config.FBX_ANIMATION_GROUP, anim[0])

    commands.select_animation(FxHelperLibrary.split_animpath(cached_anim)[0], FxHelperLibrary.split_animpath(cached_anim)[1])
