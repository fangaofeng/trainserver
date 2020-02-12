from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from ...models import Operation


class Command(BaseCommand):
    help = 'Remove obsolete permissions from the cache'

    def handle(self, *args, **options):
        for permission in Operation.objects.all():
            try:
                permission.get(
                    pk='{}.{}'.format(permission.namespace, permission.name),
                    proxy_only=True
                )
            except KeyError:
                permission.delete()
