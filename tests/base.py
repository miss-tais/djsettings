from django.test import TestCase
from django.core.cache import caches

from djsettings import djsetting


class BaseTestCase(TestCase):

    def tearDown(self):
        caches['default'].clear()

        for group in djsetting._get_registered_group_classes():
            djsetting.unregister(group)
