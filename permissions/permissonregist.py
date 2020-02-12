import warnings
from django.utils.translation import ugettext_lazy as _
from django.http import HttpRequest
from django.conf import settings
from rest_framework.request import Request
from rest_framework.settings import api_settings
from urllib.parse import urljoin
from rest_framework.schemas.generators import BaseSchemaGenerator
from rest_framework.schemas.utils import is_list_view
from rest_framework.schemas.openapi import AutoSchema
from .models import Operation, RoleFilterBackendModel
from .permissions import RolePermission, method_mapping, is_custom_action


class OperationGenerator(BaseSchemaGenerator):

    def get_operationId(self, subpath, method, view):
        """
        Return a list of keys that should be used to layout a link within
        the schema document.

        /users/                   ("users", "list"), ("users", "create")
        /users/{pk}/              ("users", "read"), ("users", "update"), ("users", "delete")
        /users/enabled/           ("users", "enabled")  # custom viewset list action
        /users/{pk}/star/         ("users", "star")     # custom viewset detail action
        /users/{pk}/groups/       ("users", "groups", "list"), ("users", "groups", "create")
        /users/{pk}/groups/{pk}/  ("users", "groups", "read"), ("users", "groups", "update"), ("users", "groups", "delete")
        """
        if hasattr(view, 'action'):
            # Viewsets have explicitly named actions.
            action = view.action
        else:
            # Views have no associated action, so we determine one from the method.
            if is_list_view(subpath, method, view):
                action = 'list'
            else:
                action = method_mapping[method.lower()]
        subprefix_path = subpath.replace(settings.REST_API_PREFIX, '', 1)
        named_path_components = [
            component for component
            in subprefix_path.strip('/').split('/')
            if '{' not in component
        ]

        if is_custom_action(action):
            # Custom action, eg "/users/{pk}/activate/", "/users/active/"
            if view.action_map and len(view.action_map) > 1:
                action = view.action_map[method.lower()]
                return '_'.join(named_path_components + [action]), action
            else:
                return '_'.join(named_path_components[:-1] + [action]), action

        return '_'.join(named_path_components + [action]), action

    def haveRolePermission(self, view):
        for permission in view.get_permissions():
            if isinstance(permission, RolePermission):
                return True
        return False

    def get_operation(self,  request=None, public=False):
        result = {}

        paths, view_endpoints = self._get_paths_and_endpoints(request)

        # Only generate the path prefix for paths that will be included
        if not paths:
            return None
        resultcount = 0
        for path, method, view in view_endpoints:
            # if the view has RolePermission,it can regist.
            if self.haveRolePermission(view):
                operationId, action = self.get_operationId(path, method, view)
                if path.startswith('/'):
                    path = path[1:]
                path = urljoin(self.url or '/', path)
                viewName = '.'.join([view.__module__, view.__class__.__name__])
                resultcount += 1
                result[operationId] = {'viewName': viewName,
                                       'method': method.lower(), 'action': action, 'path': path, 'view': view}
        if resultcount != len(result):
            print('rest api have {},but result is {}.check router path,please' % resultcount, len(result))

        return result

    def get_api(self):
        """
        OpenAPI into model.
        """
        self._initialise_endpoints()
        httprequest = HttpRequest()
        request = Request(httprequest)
        return self.get_operation(request, True)

    def update_restPermissionModel(self, request=None, public=False):
        """
        Generate a `rest permissions` into RestPermisson model.
        """
        api = self.get_api()

        for operationId, value in api.items():
            try:

                Operation.objects.update_or_create(defaults=dict(viewName=value['viewName'],
                                                                 method=value['method'],
                                                                 path=value['path'],
                                                                 action=value['action']), name=operationId
                                                   )
            except Exception as e:
                warnings.warn('update_permissionModel{} {} '.format(
                    operationId,  str(e)))

        operation_ids = api.keys()
        Operation.objects.exclude(
            name__in=operation_ids).delete()   # 删除已经不存在的

        return operation_ids
