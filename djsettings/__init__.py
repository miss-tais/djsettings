from django.utils.module_loading import autodiscover_modules

from djsettings.registries import djsetting
from djsettings.groups import DjSettingsGroup


__all__ = [
    'DjSettingsGroup', 'djsetting'
]


def autodiscover():
    autodiscover_modules('djsettings')


default_app_config = 'djsettings.apps.DjSettingsConfig'
