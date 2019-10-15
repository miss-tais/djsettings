from django.db import models
from django.utils.translation import gettext_lazy as _

from .registries import djsetting


class DjSetting(models.Model):
    name = models.CharField(_("name"),
                            max_length=255,
                            unique=True,
                            db_index=True)

    raw_value = models.TextField(_("raw value"),
                                 blank=True)

    class Meta:
        app_label = 'djsettings'
        verbose_name = _("Django Setting")
        verbose_name_plural = _("Django Settings")

    def __str__(self):
        return f"{self.name} setting"

    @property
    def value(self):
        value_instance = djsetting.get_setting(self.name)
        return value_instance.to_python(self.raw_value)

    # @value.setter
    # def value(self, value):
    #     value_instance = djsetting.get_setting(self.name)
    #     value_instance.validate(value)
    #     self.raw_value = value_instance.to_db(value)
