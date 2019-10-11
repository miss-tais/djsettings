from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

from djsettings import djsetting


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

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__}(id={self.pk!r})"

    @property
    def value(self):
        return getattr(djsetting, self.name)

    # @value.setter
    # def value(self, value):
    #     self.raw_value = self.preference.serializer.serialize(value)


#TODO: invalidate cache on model save method