from permissions.filters import RoleFilterBackend


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


class IsManagerProgressFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsManagerFilterBackend'

    def filter_queryset(self, request, queryset, view):

        if hasattr(request.user, 'managerdepartment'):
            return queryset.filter(plan__department=request.user.managerdepartment)
        else:
            return queryset.none()


class IsOwnerFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    name = 'IsOwnerFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(trainer=request.user)
