# Manages FaceFX Studio Plugins.

import FxStudio
import os
import inspect
import json


def msg(msg):
    """ Outputs a message to the FaceFX Studio log. """
    FxStudio.msg('PluginManager: {0}'.format(msg))


def warn(msg):
    """ Outputs a warning to the FaceFX Studio log. """
    FxStudio.warn('PluginManager: {0}'.format(msg))


def error(msg):
    """ Outputs an error to the FaceFX Studio log. """
    FxStudio.error('PluginManager: {0}'.format(msg))


def dev(msg):
    """ Outputs a developer trace message to the FaceFX Studio log. """
    FxStudio.dev('PluginManager: {0}'.format(msg))


class _PluginVerificationError(Exception):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


def _verify_module(module, module_name):
    """ Verfies that the module conforms to the standard FaceFX Studio plugin interface, calls the module's info function,
    and returns the info tuple. If the module does not conform to the standard FaceFX Studio plugin interface a
    _PluginVerificationError exception is raised. """
    if not hasattr(module, 'info'):
        raise _PluginVerificationError('could not find {0}.info'.format(module_name))

    if not hasattr(module, 'load'):
        raise _PluginVerificationError('could not find {0}.load'.format(module_name))

    if not hasattr(module, 'unload'):
        raise _PluginVerificationError('could not find {0}.unload'.format(module_name))

    if not callable(getattr(module, 'info')):
        raise _PluginVerificationError('{0}.info is not callable'.format(module_name))

    if not callable(getattr(module, 'load')):
        raise _PluginVerificationError('{0}.load is not callable'.format(module_name))

    if not callable(getattr(module, 'unload')):
        raise _PluginVerificationError('{0}.unload is not callable'.format(module_name))

    if len(inspect.getargspec(getattr(module, 'info'))[0]) != 0:
        raise _PluginVerificationError('{0}.info must not accept arguments'.format(module_name))

    if len(inspect.getargspec(getattr(module, 'load'))[0]) != 0:
        raise _PluginVerificationError('{0}.load must not accept arguments'.format(module_name))

    if len(inspect.getargspec(getattr(module, 'unload'))[0]) != 0:
        raise _PluginVerificationError('{0}.unload must not accept arguments'.format(module_name))

    info = getattr(module, 'info')()

    # Enforce that the info returned is a tupile of exactly
    # 3 strings.
    if not isinstance(info, tuple):
        raise _PluginVerificationError('{0}.info must return a tuple of 3 strings'.format(module_name))

    if len(info) != 3:
        raise _PluginVerificationError('{0}.info must return a tuple of 3 strings'.format(module_name))

    if not isinstance(info[0], basestring):
        raise _PluginVerificationError('{0}.info returns a tuple whose 0th element is not a string'.format(module_name))

    if not isinstance(info[1], basestring):
        raise _PluginVerificationError('{0}.info returns a tuple whose 1st element is not a string'.format(module_name))

    if not isinstance(info[2], basestring):
        raise _PluginVerificationError('{0}.info returns a tuple whose 2nd element is not a string'.format(module_name))

    return info


class Plugin:

    def __init__(self, name, path, module, version, author, description):
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.path = os.path.normcase(os.path.normpath(path))
        self.module = module
        self.loaded = False

    def __str__(self):
        return '{0} (version: {1} author: {2} description: {3} loaded: {4})'.format(self.name, self.version, self.author, self.description, self.loaded)

    def load(self):
        """ Loads the plugin if it is not already loaded. """
        if not self.loaded:
            try:
                getattr(self.module, 'load')()
                self.loaded = True
                msg('loaded plugin {0}'.format(self.name))
            except Exception as e:
                error('plugin {0} failed to load: {1}'.format(self.name, str(e)))
        else:
            dev('plugin {0} is already loaded in call to load()'.format(self.name))

    def unload(self):
        """ Unloads the plugin if it is loaded. """
        if self.loaded:
            try:
                getattr(self.module, 'unload')()
                self.loaded = False
                msg('unloaded plugin {0}'.format(self.name))
            except Exception as e:
                error('plugin {0} failed to unload: {1}'.format(self.name, str(e)))
        else:
            dev('plugin {0} is not loaded in call to unload()'.format(self.name))

    def reload(self):
        """ Reloads the plugin. If the plugin is already loaded it is first unloaded. If the plugin was not already loaded
        it is simply loaded. """
        if self.loaded:
            self.unload()

            try:
                reload(self.module)

                info = _verify_module(self.module, self.name)

                self.version = info[0]
                self.author = info[1]
                self.description = info[2]

            except _PluginVerificationError as e:
                error(str(e))
            except Exception as e:
                error('plugin {0} failed to reload: {1}'.format(self.name, str(e)))

            self.load()
        else:
            self.load()

        msg('reloaded plugin {0}'.format(self.name))

    def is_native(self):
        """ Returns True if this is a native FaceFX plugin. """
        # The module has been verified if it is in a Plugin class so there's no need to make sure
        # info exists.
        info_doc_string = getattr(getattr(self.module, 'info'), '__doc__')
        # The plugin is native if __facefx__ is found in the doc string of the info method and its author is OC3 Entertainment.
        if info_doc_string is not None and info_doc_string.find('__facefx__') != -1 and self.author == 'OC3 Entertainment':
            return True
        return False


class PluginManager:

    def __init__(self):
        self.plugins = []
        self.__search_paths = FxStudio.getSearchPath('scripts')
        self.__settings_file = os.path.normpath(os.path.join(FxStudio.getDirectory('settings'), 'plugin-settings.json'))

        # This is important! What is actually passed to connectSignal() and
        # disconnectSignal() is a method object. Each time you say self.on_app_shutdown
        # Python creates a *new* method object. In order for the connect to match up
        # with the disconnect, we need to make sure that we pass both the *same* method
        # object. Therefore we need to create only one for this instance and keep track
        # of it.
        self.appshutdown_signal_connection = self.on_app_shutdown

        FxStudio.connectSignal('appshutdown', self.appshutdown_signal_connection)

        msg('initializing...')

        self.__register_plugins(self.__scan_for_plugins())

        settings = self.load_settings()

        # If settings is empty then the python-settings.json file did not exist and we should
        # make sure that the native plugins are loaded.
        if len(settings) == 0:
            for p in self.plugins:
                if p.is_native():
                    msg('loading native plugin {0}'.format(p.name))
                    p.load()

        for d in settings:
            for p in self.plugins:
                # We could use the path to match up plugins, but running multiple installs of Studio would then
                # destroy your plugin settings each time you switch versions.  As long as the names match,
                # we try to maintain the loaded state.
                if p.name == d['name']:
                    if d['loaded'] == True:
                        p.load()

        self.save_settings()

        msg('initialized')

        self.__print_plugins()

    def __del__(self):
        FxStudio.disconnectSignal('appshutdown', self.appshutdown_signal_connection)

    def refresh(self):
        """ Refreshes the list of registered plugins. If a new plugin is found it is added and if a plugin was deleted it is
        removed. Does not call load_settings(). """
        msg('refreshing...')

        plugin_candidates = self.__scan_for_plugins()

        # For plugins that are currently loaded but are no longer on the system, unload and remove them.
        removed_plugins = []

        for p in self.plugins:
            if len([c for c in plugin_candidates if c[0] == p.name]) == 0:
                if p.loaded:
                    p.unload()
                removed_plugins.append(p)

        for p in removed_plugins:
            dev('removing missing plugin {0} at {1}'.format(p.name, p.path))
            self.plugins.remove(p)

        # Find any newly added plugins and register them.
        new_candidates = []

        for candidate in plugin_candidates:
            if len([p for p in self.plugins if p.path == candidate[1]]) == 0:
                dev('found new plugin {0} at {1}'.format(candidate[0], candidate[1]))
                new_candidates.append(candidate)

        self.__register_plugins(new_candidates)

        # If we found new native plugins load them.
        for added in new_candidates:
            for p in self.plugins:
                if p.path == added[1]:
                    if p.is_native():
                        msg('loading native plugin {0}'.format(p.name))
                        p.load()

        self.save_settings()

        msg('refreshed')

        self.__print_plugins()

    def save_settings(self):
        """ Saves the current plugin settings to the settings directory. """
        json_data = []

        for p in self.plugins:
            json_data.append({'name': p.name, 'version': p.version, 'author': p.author, 'description': p.description, 'path': p.path, 'loaded': p.loaded})

        json_file = open(self.__settings_file, 'w')
        json.dump(json_data, json_file, indent=4)
        json_file.close()

    def load_settings(self):
        """ Loads the current plugin settings from the settings directory. """
        json_data = []

        try:
            json_file = open(self.__settings_file, 'r')
            json_data = json.load(json_file)
            json_file.close()
        except:
            pass  # Ignore if the settings file was not present.

        return json_data

    def on_app_shutdown(self):
        """ The handler for the FaceFX Studio appshutdown signal. When this is triggered all currently loaded plugins are unloaded. """
        FxStudio.disconnectSignal('appshutdown', self.appshutdown_signal_connection)

        self.save_settings()

    def __print_plugins(self):
        """ Prints the currently registered plugins list to the FaceFX Studio log. """
        msg('{0} plugins:'.format(len(self.plugins)))
        for i, p in enumerate(self.plugins):
            msg('{0}: name: {1}'.format(i, p.name))
            msg('    version: {0}'.format(p.version))
            msg('    author: {0}'.format(p.author))
            msg('    description: {0}'.format(p.description))
            msg('    loaded: {0}'.format(p.loaded))

    def __scan_for_plugins(self):
        """ Scans the scripts search path and returns a list of potential plugins. """
        # Build a list of all subdirectories contained in the scripts search path.
        plugin_candidates = self.__find_plugin_candidates()

        # Only consider subdirectories that contain an __init__.py file.
        vetted_plugin_candidates = self.__vet_plugin_candidates(plugin_candidates)

        return vetted_plugin_candidates

    def __find_plugin_candidates(self):
        """ Helper for __scan_for_plugins(). """
        def __get_subdirectories(path):
            """ Helper for __find_plugin_candidates(). """
            subdirectories = (sd for sd in os.listdir(path) if os.path.isdir(os.path.join(path, sd)))
            return [(subdirectory, os.path.normcase(os.path.normpath(os.path.join(path, subdirectory)))) for subdirectory in subdirectories]

        candidates = []

        for path in self.__search_paths:
            candidates.extend(__get_subdirectories(path))

        return candidates

    def __vet_plugin_candidates(self, plugin_candidates):
        """ Returns a new list with directories not containing an __init__.py file filtered out of the plugin_candidates list. """
        return [vetted for vetted in plugin_candidates if os.path.isfile(os.path.normpath(os.path.join(vetted[1], '__init__.py')))]

    def __register_plugins(self, vetted_plugin_candidates):
        """ Registers all plugins that do not have the same name as an already registered plugin and which have passed the plugin verification step. """
        for candidate in vetted_plugin_candidates:
            # Check for duplicates.
            if len([p for p in self.plugins if p.name == candidate[0]]) > 0:
                warn('skipping registration of plugin {0} at {1} because its name collides with the already registered plugin {2} at {3}'.format(candidate[0], candidate[1], p.name, p.path))
            else:
                try:
                    module = __import__(candidate[0])

                    info = _verify_module(module, candidate[0])

                    self.plugins.append(Plugin(candidate[0], candidate[1], module, info[0], info[1], info[2]))

                    dev('registered plugin {0} at {1}'.format(candidate[0], candidate[1]))
                except ImportError as e:
                    error(str(e))
                except _PluginVerificationError as e:
                    error(str(e))
                except Exception as e:
                    error(str(e))


# The one and only plugin manager that should be used to deal with plugins.
PLUGIN_MANAGER = PluginManager()


def initialize():
    """ Add the plugin manager UI to FaceFX Studio. """
    if not FxStudio.isCommandLineMode():
        import PluginManagerUI
        PluginManagerUI.show()
