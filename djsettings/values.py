from django.core.cache import cache
from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.functional import cached_property
from django.utils.encoding import force_text
from django.db.models import signals

from .exceptions import InvalidSettingValue, SettingCachedValueNotFound, InvalidDefaultSettingValue, \
    DefaultSettingValueRequired


class empty:
    pass


class ValueDescriptor:

    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner=None):
        if instance is None:
            raise AttributeError(f"{self.value.name} is only accessible from {owner.__name__} instances.")

        try:
            return self.value.get_from_cache(self.value.name)
        except SettingCachedValueNotFound:
            pass

        db_setting = self.value.save_to_db(name=self.value.name, value=self.value.default)
        self.value.save_to_cache(db_setting)
        return self.value.to_python(db_setting.raw_value)

    def __set__(self, instance, value):
        current_value = self.__get__(instance)

        try:
            self.value.validate(self.value.prepare_value(value))
        except ValidationError as e:
            raise InvalidSettingValue(e)

        if value != current_value:
            db_setting = self.value.update_db(name=self.value.name, value=value)
            self.value.save_to_cache(db_setting)


class BaseValueType:
    form_field_class = None
    descriptor_class = ValueDescriptor

    def __init__(self, *, default=empty, required=True, widget=None, verbose_name=None, help_text='', validators=()):

        self.name = None
        self.group = None

        self._required = required
        self._widget = widget
        self._verbose_name = verbose_name
        self._help_text = help_text
        self._validators = validators
        self._empty_values = (None, '', [], (), {})

        if default is empty:
            raise DefaultSettingValueRequired

        try:
            self.validate(self.prepare_value(default))
        except ValidationError as e:
            raise InvalidDefaultSettingValue(e)

        self._default = default

    def contribute_to_class(self, cls, name):
        self.name = self.name or name
        self.group = cls
        cls._meta.add_setting(self)
        setattr(cls, self.name, self.descriptor_class(self))

    def _get_cache_key(self, name):
        return f'djsettings_{name}'

    def get_from_cache(self, name):
        cached_value = cache.get(self._get_cache_key(name), SettingCachedValueNotFound)
        if cached_value is SettingCachedValueNotFound:
            raise SettingCachedValueNotFound

        return self.to_python(cached_value)

    def save_to_cache(self, db_obj):
        cache.set(self._get_cache_key(db_obj.name), db_obj.raw_value)

    def save_to_db(self, name, value):
        from .models import DjSetting
        db_obj, created = DjSetting.objects.get_or_create(
            name=name,
            defaults={'raw_value': self.to_db(value)}
        )
        return db_obj

    def update_db(self, name, value):
        from .models import DjSetting
        db_obj, created = DjSetting.objects.update_or_create(
            name=name,
            defaults={'raw_value': self.to_db(value)}
        )
        return db_obj

    @cached_property
    def default(self):
        return self._default

    def _get_value_kwargs(self):
        return {
            'required': self._required,
            'widget': self._widget,
            'label': self._verbose_name,
            'help_text': self._help_text,
            'validators': self._validators
        }

    @cached_property
    def form_field(self):
        return self.form_field_class(**self._get_value_kwargs())

    def validate(self, value):
        self.form_field.validate(value)
        self.form_field.run_validators(value)

    def to_python(self, value):
        return self.form_field.to_python(value)

    def to_db(self, value):
        if value in self._empty_values:
            return ''
        return force_text(value)

    def prepare_value(self, value):
        return value


class BooleanValue(BaseValueType):
    form_field_class = forms.BooleanField

    def __init__(self, **kwargs):
        kwargs['required'] = False
        super().__init__(**kwargs)


class StringValue(BaseValueType):
    form_field_class = forms.CharField

    def __init__(self, *, max_length=None, min_length=None, **kwargs):
        widget = kwargs.pop('widget', widgets.Textarea)
        kwargs['widget'] = widget

        self._max_length = max_length
        self._min_length = min_length

        super().__init__(**kwargs)

    def _get_value_kwargs(self):
        value_kwargs = super()._get_value_kwargs()
        value_kwargs.update({
            'max_length': self._max_length,
            'min_length': self._min_length,
        })
        return value_kwargs


class DecimalValue(BaseValueType):
    form_field_class = forms.DecimalField

    def __init__(self, *, max_value=None, min_value=None, max_digits=None, decimal_places=None, **kwargs):
        self._max_value = max_value
        self._min_value = min_value
        self._max_digits = max_digits
        self._decimal_places = decimal_places

        super().__init__(**kwargs)

    def _get_value_kwargs(self):
        value_kwargs = super()._get_value_kwargs()
        value_kwargs.update({
            'max_value': self._max_value,
            'min_value': self._min_value,
            'max_digits': self._max_digits,
            'decimal_places': self._decimal_places,
        })
        return value_kwargs


class IntegerValue(BaseValueType):
    form_field_class = forms.IntegerField

    def __init__(self, *, max_value=None, min_value=None, **kwargs):
        self._max_value = max_value
        self._min_value = min_value

        super().__init__(**kwargs)

    def _get_value_kwargs(self):
        value_kwargs = super()._get_value_kwargs()
        value_kwargs.update({
            'max_value': self._max_value,
            'min_value': self._min_value,
        })
        return value_kwargs


class FloatValue(IntegerValue):
    form_field_class = forms.FloatField


class ModelChoiceValue(BaseValueType):
    form_field_class = forms.ModelChoiceField
    signals_handlers = {}

    def __init__(self, queryset, **kwargs):
        self._queryset = queryset
        self._model = self._queryset.model

        super().__init__(**kwargs)

        signals.pre_delete.connect(self._delete_related_value,
                                   sender=self._model)

    def _delete_related_value(self, instance, **kwargs):
        if self._default == instance:
            self._default = None

        db_setting = self.update_db(name=self.name, value=None)
        self.save_to_cache(db_setting)

    def _get_value_kwargs(self):
        value_kwargs = super()._get_value_kwargs()
        value_kwargs.update({
            'queryset': self._queryset
        })
        return value_kwargs

    def validate(self, value):
        if value is not None:
            super().validate(value)

    def prepare_value(self, value):
        if not value:
            return None
        return value.pk

    def to_db(self, value, **kwargs):
        if not value:
            return ''
        return force_text(value.pk)


__all__ = [
    'BooleanValue', 'StringValue', 'DecimalValue', 'IntegerValue', 'FloatValue'
]

