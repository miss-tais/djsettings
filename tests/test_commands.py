from django.core.management import call_command

from djsettings import djsetting, DjSettingsGroup, values
from djsettings.models import DjSetting
from djsettings.exceptions import SettingNotRegistered

from tests.base import BaseTestCase


class CommandsTestCase(BaseTestCase):
    def test_delete_old_settings_command(self):
        default = 'test'

        class TestSetting(DjSettingsGroup):
            test_string = values.StringValue(default=default)

        djsetting.register(TestSetting)

        self.assertEqual(default, djsetting.test_string)
        self.assertEqual(DjSetting.objects.all().count(), 1)
        
        djsetting.unregister(TestSetting)
        call_command('delete_old_settings')

        with self.assertRaises(SettingNotRegistered):
            djsetting.test_string = 'test 2'
        self.assertEqual(DjSetting.objects.all().count(), 0)
