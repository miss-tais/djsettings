import copy
from collections import OrderedDict

from .values import BaseValueType
from .options import Options


class DjSettingsGroupMetaclass(type):
    """Collect Settings declared in settings group."""

    def __new__(cls, name, bases, attrs):
        module = attrs.pop('__module__')
        new_attrs = {'__module__': module}

        classcell = attrs.pop('__classcell__', None)
        if classcell is not None:
            new_attrs['__classcell__'] = classcell

        attr_meta = attrs.pop('Meta', None)

        _declared_settings = []

        for obj_name, obj in attrs.items():
            if isinstance(obj, BaseValueType):
                _declared_settings.append((obj_name, obj))
            else:
                new_attrs[obj_name] = obj

        new_attrs['_declared_settings'] = OrderedDict(_declared_settings)

        new_class = super().__new__(cls, name, bases, new_attrs)

        meta = attr_meta or getattr(new_class, 'Meta', None)

        options = Options(meta)
        options.contribute_to_class(new_class, '_meta')

        # Add settings to class
        for obj_name, obj in new_class._declared_settings.items():
            obj.contribute_to_class(new_class, obj_name)

        return new_class

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        # Remember the order in which form fields are defined.
        return OrderedDict()


class DjSettingsGroup(metaclass=DjSettingsGroupMetaclass):
    """Group of settings"""

    def __repr__(self):
        return f'<{self.__class__.__name__} object>'
