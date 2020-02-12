

from rest_framework.filters import BaseFilterBackend


class IsManagerFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsManagerFilterBackend'

    def filter_queryset(self, request, queryset, view):

        if hasattr(request.user, 'managerdepartment'):
            return queryset.filter(department__slug__startswith=request.user.managerdepartment.slug)
        else:
            return queryset.none()


class IsOwnerFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    name = 'IsOwnerFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(department=request.user.department)


class IsAdminFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their all objects.
    """
    name = 'IsAdminFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset
