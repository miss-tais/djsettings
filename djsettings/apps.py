from django.apps import AppConfig


class DjSettingsConfig(AppConfig):
    name = 'djsettings'
    verbose_name = 'DjSettings'

    def ready(self):
        self.module.autodiscover()
