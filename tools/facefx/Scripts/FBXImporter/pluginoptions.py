""" Provides a class to manage interactions with the actor's python dictionary.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from time import time

import FxStudio
import config


class PluginOptions(object):
    """ Provides a fail-safe interface into the actor's python dictionary.

    This *does not* maintain the dictionaries as member variables to ensure
    that other plugin changes to the actor dictionary aren't inadvertently lost
    because we modified a cached version of the dictionary then set it back
    into the actor.

    """
    @property
    def fbx_abs_path(self):
        return self._get_option(config.FBX_ABS_PATH_KEY, '')

    @fbx_abs_path.setter
    def fbx_abs_path(self, path):
        self._set_option(config.FBX_ABS_PATH_KEY, path)

    @property
    def fbx_rel_path(self):
        return self._get_option(config.FBX_REL_PATH_KEY, '')

    @fbx_rel_path.setter
    def fbx_rel_path(self, path):
        self._set_option(config.FBX_REL_PATH_KEY, path)

    @property
    def betf_abs_path(self):
        return self._get_option(config.BETF_ABS_PATH_KEY,
            config.DEFAULT_BATCH_EXPORT_PATH)

    @betf_abs_path.setter
    def betf_abs_path(self, path):
        self._set_option(config.BETF_ABS_PATH_KEY, path)

    @property
    def betf_rel_path(self):
        return self._get_option(config.BETF_REL_PATH_KEY, '')

    @betf_rel_path.setter
    def betf_rel_path(self, path):
        self._set_option(config.BETF_REL_PATH_KEY, path)

    @property
    def fbx_modification_timestamp(self):
        return self._get_option(config.FBX_MODIFIED_TIMESTAMP, time())

    @fbx_modification_timestamp.setter
    def fbx_modification_timestamp(self, timestamp):
        self._set_option(config.FBX_MODIFIED_TIMESTAMP, timestamp)

    @property
    def betf_modification_timestamp(self):
        return self._get_option(config.BETF_MODIFIED_TIMESTAMP, time())

    @betf_modification_timestamp.setter
    def betf_modification_timestamp(self, timestamp):
        self._set_option(config.BETF_MODIFIED_TIMESTAMP, timestamp)

    @property
    def framerate(self):
        return self._get_option(config.FRAMERATE_KEY, 30.0)

    @framerate.setter
    def framerate(self, fps):
        self._set_option(config.FRAMERATE_KEY, float(fps))

    @property
    def keyframes(self):
        return self._get_option(config.KEYFRAMES_KEY, [])

    @keyframes.setter
    def keyframes(self, keys):
        self._set_option(config.KEYFRAMES_KEY, keys)

    @property
    def anim_dictionary(self):
        return self._get_option(config.ANIM_DICTIONARY_KEY, {})

    @anim_dictionary.setter
    def anim_dictionary(self, anim_dict):
        self._set_option(config.ANIM_DICTIONARY_KEY, anim_dict)

    def add_fbx_anim(self, fbx_anim_path, timestamp):
        """Adds an animation and its timestamp to the cache. """
        #print 'Adding fbx animation:', fbx_anim_path, timestamp
        anim_dict = self.anim_dictionary
        anim_dict[fbx_anim_path] = timestamp
        self._set_option(config.ANIM_DICTIONARY_KEY, anim_dict)

    def clear(self):
        self._set_option(config.ANIM_DICTIONARY_KEY, {})
        self._set_option(config.KEYFRAMES_KEY, [])
        self._set_option(config.BETF_MODIFIED_TIMESTAMP, None)
        self._set_option(config.BETF_REL_PATH_KEY, '')
        self._set_option(config.BETF_ABS_PATH_KEY, '')
        self._set_option(config.FBX_REL_PATH_KEY, None)
        self._set_option(config.FBX_ABS_PATH_KEY, None)
        self._set_option(config.FBX_MODIFIED_TIMESTAMP, None)

    def remove_fbx_anim(self, fbx_anim_path):
        """Removes an animation from the cache. """
        #print 'Removing fbx animation:', fbx_anim_path
        anim_dict = self.anim_dictionary
        if fbx_anim_path in anim_dict:
            del anim_dict[fbx_anim_path]
        self._set_option(config.ANIM_DICTIONARY_KEY, anim_dict)

    def get_fbx_anim_timestamp(self, fbx_anim_path):
        """Returns the last known modification time of the given path. """
        return self.anim_dictionary.get(fbx_anim_path, time())

    def get_fbx_anims_as_set(self):
        return set(self.anim_dictionary.keys())

    def _get_option(self, key_name, default_value=None):
        """ Returns an option from the importer's subdictionary. """
        actor_dict = self._get_actor_dictionary()
        plugin_dict = self._get_plugin_dictionary(actor_dict)
        return plugin_dict.get(key_name, default_value)

    def _set_option(self, key_name, new_value):
        """ Sets an option from the importer's subdictionary. """
        actor_dict = self._get_actor_dictionary()
        plugin_dict = self._get_plugin_dictionary(actor_dict)

        current_value = plugin_dict.get(key_name)
        if current_value is None or new_value != current_value:
            # Avoid unnecessary overwrites of the python dictionary.
            plugin_dict[key_name] = new_value
            self._set_plugin_dictionary(actor_dict, plugin_dict)
            self._set_actor_dictionary(actor_dict)

    def _get_actor_dictionary(self):
        """ Returns the dictionary in the actor's python blob. """
        return FxStudio.getActorPythonDictionary() or dict()

    def _set_actor_dictionary(self, actor_dict):
        """ Sets the dictionary in the actor's python blob. """
        FxStudio.setActorPythonDictionary(actor_dict)

    def _get_plugin_dictionary(self, actor_dict):
        """ Returns the plugin dictionary in the actor's dictionary. """
        return actor_dict.get(config.FBX_PLUGIN_DICTIONARY_KEY, dict())

    def _set_plugin_dictionary(self, actor_dict, plugin_dict):
        actor_dict[config.FBX_PLUGIN_DICTIONARY_KEY] = plugin_dict
