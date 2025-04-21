import logging
import sublime

# Default log level if not specified in settings
DEFAULT_LOG_LEVEL = 'warning'

# Log level for informing for logging changes
EVENT_LEVEL = logging.INFO

# Log formatter and handler
formatter = logging.Formatter(fmt="[{name}] {levelname}: {message}", style='{')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
pkg_name = __name__.split('.')[0]
package_logger = logging.getLogger(pkg_name)

# Special handling for log level setting to set it as early as possible
settings = sublime.load_settings(f"{pkg_name}.sublime-settings")
log_level = settings.get('log_level', DEFAULT_LOG_LEVEL).upper()
log_level = getattr(logging, log_level)
package_logger.setLevel(log_level)

# Prevent root logger from catching this
package_logger.propagate = False

# Local logger
logger = logging.getLogger(__name__)
initialized = False

def init(settings) -> None:
    """
    Initializes logging

    :param settings:    The settings module
    """

    # Add handler here to not add additional ones when file is saved and reloaded
    package_logger.addHandler(handler)

    logger.debug("Initializing logging.")

    s = settings.Settings(logging.getLevelName(log_level))
    s.log_level.add_on_change(__name__, _on_log_lvl_change)
    settings.init(s)

    global initialized
    initialized = True

def deinit(settings) -> None:
    """
    Deinitializes logging

    :param settings:    The settings module
    """

    logger.debug("Deinitializing logging.")

    settings.settings.log_level.clear_on_change(__name__)
    settings.deinit()
    for handler in package_logger.handlers:
        logger.debug(f"Removing log handler {handler}.")
        package_logger.removeHandler(handler)

    initialized = False

def reinit(settings) -> None:
    """
    Reinitializes logging

    :param settings:    The settings module
    """

    if initialized:
        deinit(settings)
    init(settings)

def _on_log_lvl_change(name : str, old_val : str, new_val : str) -> None:
    """
    Called when the log level is changed

    :param name:    The name of the setting changed
    :param old_val: The old log level
    :param new_val: The new log level
    """

    old_val_level = getattr(logging, old_val.upper())
    new_val_level = getattr(logging, new_val.upper())

    _settings_change_dbg_lvl = logging.INFO

    update_level = False
    if old_val_level > _settings_change_dbg_lvl:
        # The previous log level was too low for this settings change to have been logged
        if new_val_level > _settings_change_dbg_lvl:
            # and the updated log level is not high enough either
            # Temporarily increase the log level for this log entry
            package_logger.setLevel(_settings_change_dbg_lvl)
            update_level = True
        else:
            # New level is high enough, so set it directly
            package_logger.setLevel(new_val_level)
    else:
        # Old level was high enough - log first
        update_level = True

    logger.log(_settings_change_dbg_lvl,
        f"Changing log level from {old_val} to {new_val}.")

    if update_level:
        package_logger.setLevel(new_val_level)
