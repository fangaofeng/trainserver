from permissions.filters import RoleFilterBackend


class IsManagerFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsManagerFilterBackend'

    def filter_queryset(self, request, queryset, view):

        if hasattr(request.user, 'managerdepartment'):
            return queryset.filter(department__slug=request.user.managerdepartment.slug)
        else:
            return queryset.none()


class IsOwnerFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsOwnerFilterBackend'

    def filter_queryset(self, request, queryset, view):

        if hasattr(request.user, 'managerdepartment'):
            return queryset.filter(id=request.user.id)
        else:
            return queryset.none()
