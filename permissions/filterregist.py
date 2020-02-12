import warnings
from rest_framework.settings import api_settings
from .models import Operation, RoleFilterBackendModel
from rest_framework.compat import (
    URLPattern, URLResolver, coreapi, coreschema, get_original_route
)
from rest_framework.schemas.generators import EndpointEnumerator, get_pk_name


from django.utils.translation import ugettext_lazy as _
from rest_framework.schemas.coreapi import common_path,  is_list_view, is_custom_action
from .permissonregist import OperationGenerator


class RestFilterGenerator(OperationGenerator):

    def get_roles_filterbackends(self, view):
        """
        Return the `FilterSet` class used to filter the queryset.
        """
        role_filterbackend = []

        if hasattr(view, 'get_roles_filterbackends'):
            roles_filterbackends = view.get_roles_filterbackends()
        else:
            roles_filterbackends = getattr(view, 'roles_filterbackends', [])

        return roles_filterbackends

    def update_roleFilterModel(self, request=None, public=False):
        """
        Generate a `rest permissions` into RestPermisson model.
        """
        roles_filterbackends_name = []
        filterbackend_ids = []
        api = self.get_api()

        for operationId, value in api.items():

            view = value["view"]
            roles_filterbackends = self.get_roles_filterbackends(view)

            try:

                for role_filterbackend in roles_filterbackends:
                    obj, created = RoleFilterBackendModel.objects.update_or_create(
                        defaults={'name': role_filterbackend.name, 'operation_id': operationId},
                        operation_id=operationId, name=role_filterbackend.name,
                        # viewName=value['viewName'],
                        # method=value['method'],
                        # path=value['path'],
                        # action=value['action']
                    )
                    if obj:
                        filterbackend_ids.append(obj.id)
                        roles_filterbackends_name.append(".".join([operationId, role_filterbackend.name]))
            except Exception as e:
                warnings.warn(
                    'update_roleFilterBackendModel {} {}'.format(operationId, str(e)))

        RoleFilterBackendModel.objects.exclude(id__in=filterbackend_ids).delete()  # 删除不存在的过滤器

        return roles_filterbackends_name
