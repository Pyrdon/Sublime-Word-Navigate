import logging

# Local logger
logger = logging.getLogger(__name__)

import sublime

from .validators import *

class Settings():
    def __init__(self):
        self._settings_file = sublime.load_settings(f"{__name__.split('.')[0]}.sublime-settings")
        self._settings_file.add_on_change(__package__, self._on_settings_change)

        self._settings = SettingsList()

    def deinit(self):
        logger.debug("Deleting settings.")
        self._settings_file.clear_on_change(__package__)
        # for name, setting in self._settings.items():
        #     setting.clear_on_change()

    def __getattr__(self, name):
        if not name.startswith("_"):
            try:
                return self._settings[name]
            except KeyError as e:
                raise NameError(f"Nu such setting '{name}'.") from None

    def _on_settings_change(self):
        logger.debug("Reloading settings.")
        for name, setting in self._settings.items():
            try:
                setting._update(self._settings_file[name])
            except KeyError as e:
                # Just ignore all settings not in the settings file
                pass

class SettingsList(dict):
    # def __init__(self):
    #     self._settings = {}

    def add(self, setting):
        self[setting._name] = setting
        # self._settings[setting._name] = setting

class SingleSetting():
    def __init__(self, name, value, validator):
        self._name = name
        self._value = None
        self._validator = validator
        self._callbacks = {}
        self._update(str(value))

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return bool(self.value)

    @property
    def value(self):
        return self._value

    def validate(self, value):
        return self._validator.validate(value)

    def add_on_change(self, tag, callback):
        try:
            self._callbacks[tag]
        except KeyError as e:
            logger.debug(f"Adding callback '{tag}' for setting '{self._name}'.")
            self._callbacks[tag] = callback
        else:
            raise ValueError(
                f"Tag '{tag}' already registered a callback for change of setting '{self._name}'.")

    def clear_on_change(self, tag):
        try:
            self._callbacks[tag]
        except KeyError as e:
            raise ValueError(
                f"Tag '{tag}' not registered a callback for change of setting '{self._name}'.")
        else:
            logger.debug(f"Removing callback '{tag}' for setting '{self._name}'.")
            del self._callbacks[tag]

    def _update(self, value):
        if str(value).lower() != str(self._value).lower():
            encoded_value = self.validate(value)
            if encoded_value is not None:
                logger.debug(f"Changed setting '{self._name}' from '{self._value}' to '{encoded_value}'.")
                old_value = self._value
                self._value = encoded_value
                for k, v in self._callbacks.items():
                    v(self._name, old_value, self._value)
            else:
                raise ValueError(
                    f"Value '{value}' for setting '{self._name}' not supported. "
                    f"Allowed values are {self._validator.allowed_values_as_string}.")

class EnumSetting(SingleSetting):
    def __init__(self, name, allowed_values, value):
        super().__init__(name, value, ListValidator(allowed_values))

class LogLevelSetting(EnumSetting):
    def __init__(self, name, value):
        super().__init__(name, ['debug','info','warning','error'], value)

    def encode(self, value):
        if value is None:
            return None
        return getattr(logging, value.upper())

class IntegerRangeSetting(SingleSetting):
    def __init__(self, name, value, minimum, maximum):
        super().__init__(name, value, IntegerRangeValidator(minimum, maximum))

class BooleanSetting(SingleSetting):
    def __init__(self, name, value):
        super().__init__(name, value, BooleanValidator())
