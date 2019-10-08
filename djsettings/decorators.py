def register():
    """
    Registers the given setting(s) classes

    @djsettings.register()
    class AWSSettings(djsettings.DjSettingsGroup):
        pass

    If the setting key is already registered, this will raise an exception.
    """
    from djsettings.registries import djsetting
    from djsettings.groups import DjSettingsGroup

    def wrapper(cls):
        if not issubclass(cls, DjSettingsGroup):
            raise ValueError('Wrapped class must subclass DjSettingsGroup.')

        djsetting.register(cls)

        return cls

    return wrapper
