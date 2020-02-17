
from django.core.exceptions import PermissionDenied
import re
from rest_framework.schemas.generators import _PATH_PARAMETER_COMPONENT_RE
from rest_framework.permissions import BasePermission

from django.contrib.admindocs.views import simplify_regex
from rest_framework.settings import api_settings
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.schemas.utils import is_list_view
from django.contrib.auth import get_user_model
from .models import Operation


def is_custom_action(action):
    return action not in {
        'retrieve', 'list', 'create', 'update', 'partial_update', 'destroy'
    }


method_mapping = {
    'get': 'retrieve',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
}


class RolePermission(BasePermission):
    """
    First :user is authenticated
    Second:roles of user can get this api
    """

    def invalidate_cache(self):
        self._rest_perm_cache = {}

    def get_path_from_regex(self, path_regex):
        path = simplify_regex(path_regex)

        # Strip Django 2.0 convertors as they are incompatible with uritemplate format
        return re.sub(_PATH_PARAMETER_COMPONENT_RE, r'{\g<parameter>}', path)

    def is_list_view(self, method, view):
        """
        Return True if the given path/method appears to represent a list view.
        """
        if hasattr(view, 'action'):
            # Viewsets have an explicitly defined action, which we can inspect.
            return view.action == 'list'

        if method.lower() != 'get':
            return False
        if isinstance(view, RetrieveModelMixin):
            return False
        # if isinstance(view, ListModelMixin):
        #     return True
        # have bug
        return True

    def get_action(self,  method, view):
        """
        Return a list of keys that should be used to layout a link within
        the schema document.

        """
        if hasattr(view, 'action'):
            # Viewsets have explicitly named actions.
            action = view.action
        else:
            # Views have no associated action, so we determine one from the method.
            if self.is_list_view(method, view):
                action = 'list'
            else:
                action = method_mapping[method.lower()]

        if is_custom_action(action):
            # Custom action, eg "/users/{pk}/activate/", "/users/active/"
            if view.action_map and len(view.action_map) > 1:
                action = view.action_map[method.lower()]
        return action

    def has_permission(self, request, view):

        viewname = '.'.join([view.__module__, view.__class__.__name__])
        action = self.get_action(request.method, view)
        user_obj = request.user
        try:

            perm = "%s.%s" % (viewname, action)
            perms_dict = self.get_all_Operation(user_obj)
            if user_obj.is_active and perm in perms_dict:
                setattr(view, 'operationId', perms_dict[perm])
                return True
        except PermissionDenied:
            return False
        except Operation.DoesNotExist:
            return False
        else:
            return False

    def _get_roles_Operation(self, user_obj):
        user_roles_field = get_user_model()._meta.get_field('roles')
        user_roles_query = 'roles__%s' % user_roles_field.related_query_name()
        return Operation.objects.filter(**{user_roles_query: user_obj})   # 优化为启动后直接cache

    def get_all_Operation(self, user_obj):
        """
        Return the permissions of `user_obj` respectively.
        """

        if not user_obj.is_active:
            return dict()
        if user_obj.is_anonymous:
            return dict()
        rest_perm_cache = 'rest_perm_cache'
        if not hasattr(user_obj, rest_perm_cache):
            if user_obj.is_superuser:
                if hasattr(
                        api_settings, 'user_settings') and api_settings.user_settings.get(
                        'superuser_rest', False):
                    perms = Operation.objects.all()
                else:
                    return dict()
            else:
                # try:
                #     perms = self._rest_perm_cache.get(user_obj.roles)
                # except KeyError:
                perms = self._get_roles_Operation(user_obj)
            perms = perms.values_list('viewName', 'action', 'name').order_by()
            setattr(user_obj, rest_perm_cache, {"%s.%s" % (viewName, action): "{}".format(name) for viewName,
                                                action, name in perms})
        return getattr(user_obj, rest_perm_cache)
