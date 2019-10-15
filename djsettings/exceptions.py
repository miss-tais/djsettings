class SettingAlreadyRegistered(Exception):
    """Raise exception when settings key already registered"""


class SettingNotRegistered(Exception):
    """Raise exception when settings key not found in registry"""


class SettingsGroupClassNotRegistered(Exception):
    """Raise exception when settings group class not found in registry"""


class SettingCachedValueNotFound(Exception):
    """Raise exception when cached value not found in cache"""


class InvalidSettingValue(ValueError):
    """Raise exception when value for settings key is invalid"""


class InvalidDefaultSettingValue(ValueError):
    """Raise exception when default value for settings key is invalid"""


class DefaultSettingValueRequired(ValueError):
    """Raise exception when default value for settings key is required"""
