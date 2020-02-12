from permissions.filters import RoleFilterBackend


class IsOwnerFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsOwnerFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(recipient=request.user)


class IsOwnerFilterTaskBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsOwnerFilterBackend'

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(creater=request.user)
