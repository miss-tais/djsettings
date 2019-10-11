import six
import decimal

from django.contrib.auth.models import User

from djsettings import djsetting, DjSettingsGroup, values
from djsettings.models import DjSetting

from .base import BaseTestCase


class TestAdmin(BaseTestCase):
    def setUp(self):
        super(TestAdmin, self).setUp()

        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin_pwd')

        @djsetting.register
        class TestSettings(DjSettingsGroup):
            test_string = values.StringValue(default='test string setting', verbose_name='Test string name',
                                             help_text='test sting help text')
            test_boolean = values.BooleanValue(default=False)
            test_integer = values.IntegerValue(default=1)
            test_decimal = values.DecimalValue(default=decimal.Decimal(0.01))
            test_float = values.FloatValue(default=0.01)
            test_model_choice = values.ModelChoiceValue(queryset=User.objects.all(), default=self.user)

            class Meta:
                verbose_name = 'Test settings'

        @djsetting.register
        class TestOptionalSettings(DjSettingsGroup):
            test_string_optional = values.StringValue(default=None, required=False)
            test_integer_optional = values.IntegerValue(default=None, required=False)
            test_decimal_optional = values.DecimalValue(default=None, required=False)
            test_float_optional = values.FloatValue(default=None, required=False)
            test_model_choice_optional = values.ModelChoiceValue(queryset=User.objects.all(), default=None, required=False)

            class Meta:
                verbose_name = 'Test optional settings'

    def test_changelist(self):
        response = self.client.get('/admin/djsettings/djsetting/')
        self.assertRedirects(response, '/admin/login/?next=/admin/djsettings/djsetting/')

        self.client.login(username='admin', password='admin_pwd')

        self.user.is_staff = False
        self.user.save()

        response = self.client.get('/admin/djsettings/djsetting/')
        self.assertRedirects(response, '/admin/login/?next=/admin/djsettings/djsetting/')

        self.user.is_staff = True
        self.user.save()

        response = self.client.get('/admin/djsettings/djsetting/')
        self.assertTemplateUsed(response, 'admin/djsettings/change_list.html')

        self.assertEqual(response.context[0]['app_label'], 'djsettings')
        self.assertNotEqual(len(response.context[0]['form'].fields), 0)
        self.assertNotEqual(DjSetting.objects.all().count(), 0)
        self.assertContains(response, '<h2>Test settings</h2>')
        self.assertContains(response, 'Test string name')
        self.assertContains(response, 'test sting help text')

    def test_submit(self):
        user2 = User.objects.create_user('test_user')

        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_string': 'test_string updated',
            'test_boolean': True,
            'test_integer': 2,
            'test_decimal': decimal.Decimal(0.02),
            'test_float': 0.02,
            'test_model_choice': user2.id,
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        db_djsettings = dict(DjSetting.objects.all().values_list('name', 'raw_value'))

        for key in dir(djsetting):
            if key == 'test_model_choice':
                self.assertEqual(db_djsettings[key], six.text_type(user2.pk))
                self.assertEqual(getattr(djsetting, key), user2)
            elif key in data:
                self.assertEqual(db_djsettings[key], six.text_type(data[key]))
                self.assertEqual(getattr(djsetting, key), data[key])
            else:
                value = getattr(djsetting, key)
                self.assertEqual(db_djsettings[key], '' if not value else value)

    def test_required_field_submit(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_string': '',
            'test_boolean': False,
            'test_integer': '',
            'test_decimal': '',
            'test_float': '',
            'test_model_choice': '',
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        for key in dir(djsetting):
            if key == 'test_boolean' or key not in data:
                self.assertTrue(key in response.context['form'].cleaned_data)
            else:
                self.assertFormError(response, 'form', key, 'This field is required.')


class TestAdminStringValue(BaseTestCase):
    def setUp(self):
        super(TestAdminStringValue, self).setUp()

        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin_pwd')
        self.max_length = 5
        self.min_length = 3

        @djsetting.register
        class TestStringValueSettings(DjSettingsGroup):
            test_string = values.StringValue(default='test', max_length=self.max_length, min_length=self.min_length)

    def test_string_max_length(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_string': 'too long'
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_string',
            f'Ensure this value has at most {self.max_length} characters (it has {len(data["test_string"])}).'
        )

    def test_string_min_length(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_string': 'a'
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_string',
            f'Ensure this value has at least {self.min_length} characters (it has {len(data["test_string"])}).'
        )


class TestAdminDecimalValue(BaseTestCase):
    def setUp(self):
        super(TestAdminDecimalValue, self).setUp()

        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin_pwd')
        self.max_value = 12
        self.min_value = 3
        self.max_digits = 4
        self.decimal_places = 2

        @djsetting.register
        class TestDecimalValueSettings(DjSettingsGroup):
            test_decimal = values.DecimalValue(default=decimal.Decimal(4),
                                               max_value=self.max_value,
                                               min_value=self.min_value,
                                               max_digits=self.max_digits,
                                               decimal_places=self.decimal_places)

    def test_decimal_max_digits(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_decimal': 10.001
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_decimal', f'Ensure that there are no more than {self.max_digits} digits in total.'
        )

    def test_decimal_decimal_places(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_decimal': 9.001
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_decimal', f'Ensure that there are no more than {self.decimal_places} decimal places.'
        )

    def test_decimal_max_value(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_decimal': 13
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_decimal', f'Ensure this value is less than or equal to {self.max_value}.'
        )

    def test_decimal_min_value(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_decimal': 2
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_decimal', f'Ensure this value is greater than or equal to {self.min_value}.'
        )

    def test_integer_is_number(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_decimal': '3a'
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_decimal', f'Enter a number.'
        )


class TestAdminFloatValue(BaseTestCase):
    def setUp(self):
        super(TestAdminFloatValue, self).setUp()

        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin_pwd')
        self.max_value = 12.5
        self.min_value = 3.5

        @djsetting.register
        class TestFloatValueSettings(DjSettingsGroup):
            test_float = values.FloatValue(default=4.5,
                                           max_value=self.max_value,
                                           min_value=self.min_value)

    def test_float_max_value(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_float': 12.6
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_float', f'Ensure this value is less than or equal to {self.max_value}.'
        )

    def test_float_min_value(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_float': 3.4
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_float', f'Ensure this value is greater than or equal to {self.min_value}.'
        )

    def test_integer_is_number(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_float': '3a'
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_float', f'Enter a number.'
        )


class TestAdminIntegerValue(BaseTestCase):
    def setUp(self):
        super(TestAdminIntegerValue, self).setUp()

        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin_pwd')
        self.max_value = 12
        self.min_value = 3

        @djsetting.register
        class TestIntegerValueSettings(DjSettingsGroup):
            test_integer = values.IntegerValue(default=4,
                                               max_value=self.max_value,
                                               min_value=self.min_value)

    def test_integer_max_value(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_integer': 13
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_integer', f'Ensure this value is less than or equal to {self.max_value}.'
        )

    def test_integer_min_value(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_integer': 2
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_integer', f'Ensure this value is greater than or equal to {self.min_value}.'
        )

    def test_integer_whole_number(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_integer': 5.01
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_integer', f'Enter a whole number.'
        )

    def test_integer_is_number(self):
        self.client.login(username='admin', password='admin_pwd')

        data = {
            'test_integer': '3a'
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_integer', f'Enter a whole number.'
        )


class TestAdminModelChoiceValue(BaseTestCase):
    def setUp(self):
        super(TestAdminModelChoiceValue, self).setUp()

        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin_pwd')

        @djsetting.register
        class TestModelChoiceSettings(DjSettingsGroup):
            test_model_choice = values.ModelChoiceValue(queryset=User.objects.filter(is_staff=True),
                                                        default=self.user)

    def test_invalid_choice(self):
        self.client.login(username='admin', password='admin_pwd')

        new_user = User.objects.create_user('new_user')

        data = {
            'test_model_choice': new_user
        }

        response = self.client.post('/admin/djsettings/djsetting/', data=data)
        self.assertIs(response.status_code, 200)

        self.assertFormError(
            response, 'form', 'test_model_choice',
            'Select a valid choice. That choice is not one of the available choices.'
        )
