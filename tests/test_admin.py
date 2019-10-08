from django.contrib.auth.models import User
from django.test import TestCase
from django.core.cache import caches

from djsettings import djsetting
from djsettings.models import DjSetting


class TestAdmin(TestCase):
    def setUp(self):
        super(TestAdmin, self).setUp()
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin_pwd')

    def tearDown(self):
        caches['default'].clear()

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
        self.assertContains(response, '<h2>Test string setting</h2>')
        self.assertContains(response, '<h2>Test boolean setting</h2>')

    # def test_submit(self):
    #     self.client.login(username='admin', password='admin_pwd')
    #
    #     response = self.client.get('/admin/djsettings/djsetting/')
    #     print(DjSetting.objects.all())
    #     response = self.client.post('/admin/djsettings/djsetting/', data={'test_string': 'test_string updated'})
    #     print(response)
    #     print(response.status_code)
    #     print(DjSetting.objects.filter(name='test_string').first().raw_value)
    #     self.assertEqual(djsetting.test_string, 'test_string updated')
    #
    # def test_required_field_submit(self):
    #     self.client.login(username='admin', password='admin_pwd')
    #
    #     response = self.client.get('/admin/djsettings/djsetting/')
    #     print(DjSetting.objects.all())
    #     response = self.client.post('/admin/djsettings/djsetting/', data={'test_string': ''})
    #     print(response.context[0]['form'].fields['test_string'])
    #     self.assertTrue('error_messages' in response.context[0]['form'].fields['test_string'])
    #     self.assertTrue('required' in response.context[0]['form'].fields['test_string']['error_messages'])
