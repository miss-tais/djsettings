from django.core.management.base import BaseCommand

from djsettings.registries import djsetting
from djsettings.models import DjSetting


class Command(BaseCommand):
    help = 'Delete old settings from database'

    def handle(self, *args, **options):
        DjSetting.objects.exclude(name__in=dir(djsetting)).delete()

