from .exceptions import SettingAlreadyRegistered, SettingNotRegistered
from .groups import DjSettingsGroup


class DjSettingsRegistry:
    __initialized = False
    
    __registered_groups = {}
    __registered_keys = {}
    __registered_values = {}

    def __init__(self, *args, **kwargs):
        self.__initialized = True

    def register(self, settings_group_cls):
        if not issubclass(settings_group_cls, DjSettingsGroup):
            raise ValueError('Wrapped class must subclass DjSettingsGroup.')

        settings_group = settings_group_cls()

        self.__registered_groups[settings_group_cls] = settings_group

        for setting in settings_group:
            if setting.name in self.__registered_keys:
                raise SettingAlreadyRegistered(f'Setting "{setting.name}" is already registered')

            self.__registered_keys[setting.name] = settings_group
            self.__registered_values[setting.name] = setting

    def unregister(self, settings_group_cls):
        if settings_group_cls in self.__registered_groups:
            del self.__registered_groups[settings_group_cls]

        for setting_name in settings_group_cls._declared_settings:
            if setting_name in self.__registered_keys:
                del self.__registered_keys[setting_name]

            if setting_name in self.__registered_values:
                del self.__registered_values[setting_name]

    def __dir__(self):
        return self.__registered_keys.keys()

    def __getattr__(self, name):
        if name in self.__registered_keys:
            return getattr(self.__registered_keys[name], name)

        super().__getattr__(name)

    def __setattr__(self, name, value):
        if self.__initialized and not hasattr(self, name):
            raise SettingNotRegistered
        else:
            if name in self.__registered_keys:
                setattr(self.__registered_keys[name], name, value)
            else:
                super().__setattr__(name, value)

    def get_all_setting_groups(self):
        return self.__registered_groups.values()

    # used in tests
    def get_setting(self, name):
        if name not in self.__registered_values:
            raise SettingNotRegistered
        return self.__registered_values[name]

    # used in tests
    def _get_registered_group_classes(self):
        return list(self.__registered_groups.keys())


djsetting = DjSettingsRegistry()
