from permissions.filters import RoleFilterBackend


class IsManagerFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsManagerFilterBackend'

    def filter_queryset(self, request, queryset, view):

        if hasattr(request.user, 'managerdepartment'):
            return queryset.filter(departments=request.user.managerdepartment)
        else:
            return queryset.none()


class IsUserFilterBackend(RoleFilterBackend):
    """
    Filter that only allows users to see their manager objects by the role in department
    """
    name = 'IsUserFilterBackend'

    def filter_queryset(self, request, queryset, view):

        return queryset.filter(category='公开课')
