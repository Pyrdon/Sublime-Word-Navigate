import logging

# Local logger
logger = logging.getLogger(__name__)

from .sublime_util import settings

initialized = False

def init(settings_obj):
    """
    Initializes the settings module

    :param settings:    The settings object
    """

    logger.debug("Initializing setting.")
    global settings
    settings = settings_obj

    global initialized
    initialized = True

def deinit():
    """
    Deinitializes the settings module
    """

    logger.debug("Deinitializing setting.")
    global settings
    # Deinitialize the settings (instead of deleting it, as __del__ won't be run until GC runs it)
    settings.deinit()
    initialized = False

def reinit():
    """
    Reinitializes the settings module
    """

    if initialized:
        deinit()
    init()

class Settings(settings.Settings):
    """
    Class representing settings for the plugin
    """

    def __init__(self, default_log_level):
        """
        Initializes settings

        :param default_log_level: The default log level
        """

        super().__init__()

        # Add all settings with their default values
        self._settings.add(settings.LogLevelSetting('log_level', default_log_level))
        self._settings.add(settings.BooleanSetting('use_index', True))
        self._settings.add(settings.BooleanSetting('allow_multiple_words', True))
        self._settings.add(settings.BooleanSetting('expand_first', True))
        self._settings.add(settings.BooleanSetting('wrap_buffer', True))
        self._settings.add(settings.BooleanSetting('wrap_line', True))
        self._settings.add(settings.BooleanSetting('case_sensitive', False))

        # Call this once on creation to set it up
        self._on_settings_change()
