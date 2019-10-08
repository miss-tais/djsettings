from django.db import models
from django.utils.translation import gettext_lazy as _


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
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
