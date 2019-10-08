from .exceptions import SettingAlreadyRegistered, SettingNotRegistered, SettingCachedValueNotFound


class DjSettingsRegistry:
    __initialized = False
    
    __registered_groups = []
    __registered_keys = {}
    __registered_values = {}

    def __init__(self, *args, **kwargs):
        self.__initialized = True

    def register(self, settings_group_cls):
        settings_group = settings_group_cls()

        self.__registered_groups.append(settings_group)

        for setting in settings_group:
            if setting.name in self.__registered_keys:
                raise SettingAlreadyRegistered(f'Setting "{setting.name}" is already registered')

            self.__registered_keys[setting.name] = settings_group
            self.__registered_values[setting.name] = setting

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

    def get_all_settings(self):
        return self.__registered_values.values()

    def get_all_setting_groups(self):
        return self.__registered_groups


djsetting = DjSettingsRegistry()
