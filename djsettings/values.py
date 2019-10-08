from django.core.cache import cache
from django.utils import six
from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.functional import cached_property

from .exceptions import InvalidSettingValue, SettingCachedValueNotFound, InvalidDefaultSettingValue


class BaseValueType:
    form_field_class = None

    def __init__(self, default, required=True, widget=None, verbose_name=None,
                 help_text='', error_messages=None, validators=(), additional_value_kwargs=()):

        self.value_kwargs = {
            'required': required,
            'widget': widget,
            'label': verbose_name,
            'help_text': help_text,
            'error_messages': error_messages,
            'validators': validators
        }
        self.value_kwargs.update(dict(additional_value_kwargs))

        try:
            default = self.to_python(default)
            self.validate(default)
        except ValidationError as e:
            raise InvalidDefaultSettingValue(e)
        self._default = default

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            raise AttributeError(f"{self.name} is only accessible from {owner.__name__} instances.")

        try:
            return self._get_from_cache(self.name)
        except SettingCachedValueNotFound:
            pass

        db_setting = self._save_to_db(name=self.name, value=self.default)
        self._save_to_cache(db_setting)
        return self.to_python(db_setting.raw_value)

    def __set__(self, instance, value):
        current_value = self.__get__(instance)

        try:
            new_value = self.to_python(value)
            self.validate(new_value)
        except ValidationError as e:
            raise InvalidSettingValue(e)

        if new_value != current_value:
            db_setting = self._update_db(name=self.name, value=value)
            self._save_to_cache(db_setting)

    def _get_cache_key(self, name):
        return f'djsettings_{name}'

    def _get_from_cache(self, name):
        cached_value = cache.get(self._get_cache_key(name), SettingCachedValueNotFound)
        if cached_value is SettingCachedValueNotFound:
            raise SettingCachedValueNotFound

        return self.to_python(cached_value)

    def _save_to_cache(self, db_obj):
        cache.set(self._get_cache_key(db_obj.name), db_obj.raw_value)

    def _save_to_db(self, name, value):
        from .models import DjSetting
        db_obj, created = DjSetting.objects.get_or_create(
            name=name,
            defaults={'raw_value': self.to_db(value)}
        )
        return db_obj

    def _update_db(self, name, value):
        from .models import DjSetting
        db_obj, created = DjSetting.objects.update_or_create(
            name=name,
            defaults={'raw_value': self.to_db(value)}
        )
        return db_obj

    @cached_property
    def form_field(self):
        return self.form_field_class(**self.value_kwargs)

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        value = self.to_python(value)
        self.validate(value)

        self._default = value

    def validate(self, value):
        self.form_field.validate(value)
        self.form_field.run_validators(value)

    def to_python(self, value):
        return self.form_field.to_python(value)

    def to_db(self, value):
        return six.text_type(value)


class BooleanValue(BaseValueType):
    form_field_class = forms.BooleanField

    def __init__(self, default, **kwargs):
        kwargs['required'] = False
        super().__init__(default, **kwargs)


class StringValue(BaseValueType):
    form_field_class = forms.CharField

    def __init__(self, default, max_length=None, min_length=None, **kwargs):
        widget = kwargs.pop('widget', widgets.Textarea)
        kwargs['additional_value_kwargs'] = (
            ('max_length', max_length),
            ('min_length', min_length),
            ('widget', widget)
        )
        super().__init__(default, **kwargs)


class DecimalValue(BaseValueType):
    form_field_class = forms.DecimalField

    def __init__(self, default, max_value=None, min_value=None, max_digits=None, decimal_places=None, **kwargs):
        kwargs['additional_value_kwargs'] = (
            ('max_value', max_value),
            ('min_value', min_value),
            ('max_digits', max_digits),
            ('decimal_places', decimal_places)
        )
        super().__init__(default, **kwargs)


class IntegerValue(BaseValueType):
    form_field_class = forms.IntegerField

    def __init__(self, default, max_value=None, min_value=None, **kwargs):
        kwargs['additional_value_kwargs'] = (
            ('max_value', max_value),
            ('min_value', min_value),
        )
        super().__init__(default, **kwargs)


class FloatValue(IntegerValue):
    form_field_class = forms.FloatField


__all__ = [
    'BooleanValue', 'StringValue', 'DecimalValue', 'IntegerValue', 'FloatValue'
]

