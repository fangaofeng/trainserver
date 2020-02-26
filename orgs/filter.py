

from rest_framework.filters import BaseFilterBackend
from .models import Department


class IsManagerFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsManagerFilterBackend'

    def filter_queryset(self, request, queryset, view):

        if hasattr(request.user, 'managerdepartment'):
            if view.action == 'list':
                if not (request.query_params.get('id', None) or request.query_params.get('slug', None) or
                        request.query_params.get('name', None)):
                    return queryset.filter(id=request.user.managerdepartment.id)
            return queryset.filter(slug__startswith=request.user.managerdepartment.slug)
        else:
            return queryset.none()


class IsUserFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    name = 'IsUserFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(id=request.user.department.id)


class IsAdminFilterBackend(BaseFilterBackend):
    """
    Filter that only allows admin to see their all objects.
    """
    name = 'IsAdminFilterBackend'

    def filter_queryset(self, request, queryset, view):
        if view.action == 'list':
            if not (request.query_params.get('id', None) or request.query_params.get('slug', None) or
                    request.query_params.get('name', None)):
                return Department.objects.root_nodes()

        return queryset
