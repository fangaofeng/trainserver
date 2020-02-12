

from rest_framework.filters import BaseFilterBackend
from permissions.models import RoleFilterBackendModel, RoleOperationshipWithFilter
import warnings
import rest_framework_filters as filters
# from django_filters import rest_framework as filters
from orgs.models import Department
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model

BOOLEAN_CHOICES = (('false', 'False'), ('true', 'True'),)


class WhlRestFilterBackend(filters.backends.RestFrameworkFilterBackend):
    # def get_filterset_kwargs(self, request, queryset, view):
    #     return {
    #         'data': request.query_params,
    #         'queryset': queryset,
    #         'request': request,
    #         'view_kwargs': view.kwargs
    #     }

    def get_filterset(self, request, queryset, view):
        filterset_instance = super().get_filterset(request, queryset, view)
        if filterset_instance:
            setattr(filterset_instance, 'view_kwargs', view.kwargs)
        return filterset_instance


class RoleFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    name = __name__

    def _get_roles_operations(self, user_obj, operationId):
        user_roles_field = get_user_model()._meta.get_field('roles')
        user_roles_query = 'roles__%s' % user_roles_field.related_query_name()
        yy = RoleFilterBackendModel.objects.filter(**{'roles__role__in': user_obj.roles.all(),
                                                      "operation_id": operationId})
        return RoleOperationshipWithFilter.objects.filter(
            **{'role__in': user_obj.roles.all(),
               "operation_id": operationId})
        # 需要修改为根据角色首先and角色内过滤条件，然后role之间or过滤条件，否则对于多角色用户无法支持。优化，使用set的and方法去除多余的name优化过滤调教

    def get_operation_filterbackends_name(self, user_obj, view):
        """
        Return the filterbackend name list of `user_obj` respectively.
        """
        filterbackends = []
        rest_filter_cache = 'rest_filter_cache'
        if not hasattr(user_obj, rest_filter_cache):
            if hasattr(view, 'operationId'):
                rolefilterbackends = self._get_roles_operations(user_obj, view.operationId)
                # print(rolefilterbackends)
                for filterback in rolefilterbackends:
                    # print(filterback.filters.all())
                    filterbackends.append(set([name
                                               for name in filterback.filters.values_list('name', flat=True).order_by(
                                                   'name')]))

            setattr(user_obj, rest_filter_cache, filterbackends)
        return getattr(user_obj, rest_filter_cache)

    def get_view_filterbackends(self, request, view):
        """
        Return the `FilterSet` class used to filter the queryset.
        """
        roles_filterbackends = []
        if hasattr(view, 'get_roles_filterbackends'):
            _role_filterbackends = view.get_roles_filterbackends()
        else:
            _role_filterbackends = getattr(view, 'roles_filterbackends', [])
        filterbackend_dict = {value.name: value for value in _role_filterbackends}
        filterbackends_name = self.get_operation_filterbackends_name(request.user, view)  # 多个角色

        for filternames in filterbackends_name:
            role_filter = []
            for name in filternames:
                role_filter.append(filterbackend_dict[name])
            roles_filterbackends.append(role_filter)
        return roles_filterbackends

    def get_roles_queryset(self, request, queryset, view):

        if not request.user.is_active or request.user.is_anonymous:
            return queryset.none()
        if request.user.is_superuser:
            if hasattr(
                    api_settings, 'user_settings') and api_settings.user_settings.get(
                    'superuser_rest', False):
                return queryset
            else:
                return queryset.none()

        roles_filterbackends = self.get_view_filterbackends(request, view)
        queryset_T = None
        for role_filterbackends in roles_filterbackends:
            queryset_t2 = None
            for filter in role_filterbackends:
                queryset_t1 = filter().filter_queryset(request, queryset, view)
                if queryset_t2:
                    queryset_t2 = queryset_t2 & queryset_t1
                else:
                    queryset_t2 = queryset_t1
            if queryset_T:
                queryset_T = queryset_t2 | queryset_T
            else:
                queryset_T = queryset_t2
        if queryset_T is None:
            queryset_T = queryset
        return queryset_T

    def filter_queryset(self, request, queryset, view):
        return self.get_roles_queryset(request, queryset, view)


class IsManagerFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsManagerFilterBackend'

    def filter_queryset(self, request, queryset, view):

        if hasattr(request.user, 'managerdepartment'):
            return queryset.filter(department=request.user.managerdepartment)
        else:
            return queryset.none()


class IsOwnerFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    name = 'IsOwnerFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class IsAdminFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their all objects.
    """
    name = 'IsAdminFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset
