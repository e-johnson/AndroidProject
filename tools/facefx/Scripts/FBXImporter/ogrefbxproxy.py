"""Proxies nasty ogre fbx commandline utility calls behind nice functions.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import re
import os
import json
import subprocess
import tempfile

import config
from helper import get_render_asset_name, get_animation_name_from_path
from fbximporterror import FBXImportError
from pluginoptions import PluginOptions


class OgreFBXProxy:
    """Proxies calls into the OgreFBX command-line utility.

    """
    def __init__(self):
        self.clip_data = {}

    def create_render_asset(self, fbx_path, export_anim=None):
        """Runs the fbx converter on the file specified.

        After running, the clip_data member dict contains the dictionary parsed
        from the ANIMATION={...} json in the output of OgreFBX.

        """
        if export_anim is None:
            export_anim = True

        render_asset_name = get_render_asset_name(fbx_path)

        with self._create_temp_log_file() as log_file:
            arguments = [config.OGREFBX_PATH,
                '-t',  # copy textures, takes no args.
                '-f', fbx_path,
                '-o', self._get_output_path(render_asset_name, '.MESH'),
                '-l', config.OGREFBX_LOG_PATH]
            if export_anim:
                arguments.extend([
                    '-e', config.POSE_ANIM_NAME,
                    '-z', config.FRAME_ZERO_ANIM_NAME])

            return_code = subprocess.call(arguments, stdout=log_file,
                stderr=log_file, stdin=subprocess.PIPE, startupinfo=self._get_startupinfo())

            if 0 != return_code:
                raise FBXImportError('Call to FxOgreFBX failed to import mesh!')

        if export_anim:
            # Only update cached anim data when the log is exported
            self._parse_log()

        self._remove_log()

    def import_animation(self, fbx_anim_path, render_asset_name, update_cache):
        """Imports an animation from the given FBX to the render asset.

        After running, the clip_data member dict contains the dictionary parsed
        from the ANIMATION={...} json in the output of OgreFBX.

        """
        with self._create_temp_log_file() as log_file:
            return_code = subprocess.call(
                [config.OGREFBX_PATH,
                    '-f', fbx_anim_path,
                    '-s', self._get_output_path(render_asset_name, '.SKELETON'),
                    '-m', self._get_output_path(render_asset_name, '.MESH'),
                    '-a', get_animation_name_from_path(fbx_anim_path),
                          config.USE_FBX_START_TIME, config.USE_FBX_END_TIME,
                    '-l', config.OGREFBX_LOG_PATH],
                stdout=log_file,
                stderr=log_file,
                stdin=subprocess.PIPE,
                startupinfo=self._get_startupinfo())

            if 0 != return_code:
                raise FBXImportError('Call to FxOgreFBX failed to import animation!')

        if update_cache:
            self._parse_log()

        self._remove_log()

    def remove_animation(self, fbx_anim_path, render_asset_name):
        """Removes an animation (specified by the *old* path) from a render
        asset.

        """
        with self._create_temp_log_file() as log_file:
            return_code = subprocess.call(
                [config.OGREFBX_PATH,
                    '-s', self._get_output_path(render_asset_name, '.SKELETON'),
                    '-m', self._get_output_path(render_asset_name, '.MESH'),
                    '-d', get_animation_name_from_path(fbx_anim_path),
                    '-l', config.OGREFBX_LOG_PATH],
                stdout=log_file,
                stderr=log_file,
                stdin=subprocess.PIPE,
                startupinfo=self._get_startupinfo())

            if 0 != return_code:
                raise FBXImportError('Call to FxOgreFBX failed to remove animation!')

        self._remove_log()

    def _get_output_path(self, render_asset_name, ext):
        """Creates the output path for the command-line utility. """
        return ''.join([config.FBX_IMPORTER_CACHE_DIR, render_asset_name, ext])

    def _create_temp_log_file(self):
        """Sets up the logging for the command-line utility. """
        # Create a temporary file to hold subprocess output.
        handle, self._filename = tempfile.mkstemp()
        return os.fdopen(handle, 'w')

    def _get_startupinfo(self):
        """Returns the startupinfo structure to use with the subprocess call.

        """
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return startupinfo

    def _parse_log(self):
        """Extracts clip data from the ANIMATION={} json section of the
        log output. Saves the clip data to the options.

        """
        with open(self._filename, 'r') as f:
            log_contents = f.read()
            match = re.search(r'ANIMATION\=(\{.*\})', log_contents)
            if match:
                self.clip_data = json.loads(match.group(0).split('=')[1])

                options = PluginOptions()
                if 'fps' in self.clip_data:
                    options.framerate = self.clip_data['fps']
                if 'keys' in self.clip_data:
                    options.keyframes = self.clip_data['keys']

    def _remove_log(self):
        """Removes the log file from the system. """
        os.remove(self._filename)
