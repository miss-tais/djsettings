import copy
from collections import OrderedDict

from django.utils.functional import cached_property

from .values import BaseValueType
from .options import Options


class DjSettingsGroupMetaclass(type):
    def __new__(cls, name, bases, attrs):
        module = attrs.pop('__module__')
        new_attrs = {'__module__': module}

        classcell = attrs.pop('__classcell__', None)
        if classcell is not None:
            new_attrs['__classcell__'] = classcell

        attr_meta = attrs.pop('Meta', None)

        _declared_settings = []
        for setting_name, obj in attrs.items():
            if isinstance(obj, BaseValueType):
                _declared_settings.append((setting_name, obj))

            new_attrs[setting_name] = obj

        new_attrs['_declared_settings'] = OrderedDict(_declared_settings)

        new_class = super().__new__(cls, name, bases, new_attrs)

        meta = attr_meta or getattr(new_class, 'Meta', None)

        options = Options(meta)
        options.contribute_to_class(new_class, '_meta')

        return new_class


class DjSettingsGroup(metaclass=DjSettingsGroupMetaclass):
    def __init__(self):
        self.settings = copy.deepcopy(self._declared_settings)

    def __iter__(self):
        for name in self.settings:
            yield self[name]

    def __getitem__(self, name):
        try:
            field = self.settings[name]
        except KeyError:
            available_settings = ', '.join(sorted(s for s in self.settings))
            raise KeyError(f"Key '{name}' not found in '{self.__class__.__name__}'. Choices are: {available_settings}.")
        return field
