from django.core.management.base import BaseCommand


from ...permissonregist import OperationGenerator
from ...filterregist import RestFilterGenerator


class Command(BaseCommand):
    help = 'add perission permissions to the database'

    def handle(self, *args, **options):

        permissions = OperationGenerator().update_restPermissionModel()
        print('permissions count is {}'.format(len(permissions)))
        rolefilters = RestFilterGenerator().update_roleFilterModel()
        print('rolefilters count is {}'.format(len(rolefilters)))
