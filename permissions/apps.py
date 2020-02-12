from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _


from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    has_rest_api = True
    has_tests = True
    name = 'permissions'
    verbose_name = _('permissions')

    def ready(self):
        pass
        # from .permissonregist import OperationGenerator
        # from .filterregist import RestFilterGenerator
        # permissions = OperationGenerator().update_restPermissionModel()
        # rolefilters = RestFilterGenerator().update_roleFilterModel()

        # print('permissions count is {}'.format(len(permissions)))
        # print('rolefilters count is {}'.format(len(rolefilters)))
