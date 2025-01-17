import decimal

from django.contrib.auth.models import User
from django.core.cache import caches

from djsettings import djsetting, DjSettingsGroup, values
from djsettings.models import DjSetting
from djsettings.exceptions import InvalidSettingValue

from .base import BaseTestCase


class BaseTestValue:
    def test_default_setting(self):
        self.assertEqual(len(DjSetting.objects.filter(name=self.attr_name)), 0)
        self.assertEqual(getattr(djsetting, self.attr_name), self.default)

        db_obj = DjSetting.objects.get(name=self.attr_name)

        self.assertEqual(db_obj.value, self.default)
        dj_setting = djsetting.get_setting(self.attr_name)
        self.assertEqual(db_obj.raw_value, caches['default'].get(dj_setting._get_cache_key(self.attr_name)))

    def test_set_setting(self):
        setattr(djsetting, self.attr_name, self.new_value)

        db_obj = DjSetting.objects.get(name=self.attr_name)

        self.assertEqual(getattr(djsetting, self.attr_name), self.new_value)
        self.assertEqual(db_obj.value, self.new_value)
        dj_setting = djsetting.get_setting(self.attr_name)
        self.assertEqual(db_obj.raw_value, caches['default'].get(dj_setting._get_cache_key(self.attr_name)))

    def test_invalid_value(self):
        if hasattr(self, 'invalid_value'):
            with self.assertRaises(InvalidSettingValue):
                setattr(djsetting, self.attr_name, self.invalid_value)


class TestStringValue(BaseTestCase, BaseTestValue):
    def setUp(self):
        super(TestStringValue, self).setUp()
        self.default = 'test string'
        self.attr_name = 'test_string'
        self.new_value = 'testing string updated'
        self.invalid_value = 'test'

        @djsetting.register
        class TestSetting(DjSettingsGroup):
            test_string = values.StringValue(default=self.default, min_length=5)


class TestBooleanValue(BaseTestCase, BaseTestValue):
    def setUp(self):
        super(TestBooleanValue, self).setUp()
        self.default = True
        self.attr_name = 'test_boolean'
        self.new_value = False

        @djsetting.register
        class TestSetting(DjSettingsGroup):
            test_boolean = values.BooleanValue(default=self.default)


class TestIntegerValue(BaseTestCase, BaseTestValue):
    def setUp(self):
        super(TestIntegerValue, self).setUp()
        self.default = 1
        self.attr_name = 'test_integer'
        self.new_value = 2
        self.invalid_value = 'test'

        @djsetting.register
        class TestSetting(DjSettingsGroup):
            test_integer = values.IntegerValue(default=self.default)


class TestFloatValue(BaseTestCase, BaseTestValue):
    def setUp(self):
        super(TestFloatValue, self).setUp()
        self.default = 1.01
        self.attr_name = 'test_float'
        self.new_value = 1.05
        self.invalid_value = 'test'

        @djsetting.register
        class TestSetting(DjSettingsGroup):
            test_float = values.FloatValue(default=self.default)


class TestDecimalValue(BaseTestCase, BaseTestValue):
    def setUp(self):
        super(TestDecimalValue, self).setUp()
        self.default = decimal.Decimal(1.01)
        self.attr_name = 'test_decimal'
        self.new_value = decimal.Decimal(1.05)
        self.invalid_value = 'test'

        @djsetting.register
        class TestSetting(DjSettingsGroup):
            test_decimal = values.DecimalValue(default=self.default)


class TestModelChoiceValue(BaseTestCase, BaseTestValue):
    def setUp(self):
        super(TestModelChoiceValue, self).setUp()
        self.default = User.objects.create_user('test')
        self.attr_name = 'test_model_choice'
        self.new_value = User.objects.create_user('test2')
        self.invalid_value = 'test'

        @djsetting.register
        class TestSetting(DjSettingsGroup):
            test_model_choice = values.ModelChoiceValue(queryset=User.objects.all(), default=self.default)

    def test_obj_deleted(self):
        self.assertEqual(getattr(djsetting, self.attr_name), self.default)

        setattr(djsetting, self.attr_name, self.new_value)
        self.assertEqual(getattr(djsetting, self.attr_name), self.new_value)

        self.new_value.delete()
        self.assertEqual(getattr(djsetting, self.attr_name), None)

    def test_default_obj_deleted(self):
        self.default.delete()
        self.assertEqual(getattr(djsetting, self.attr_name), None)
