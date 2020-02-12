from rest_framework import mixins, views
from rest_framework import viewsets
from permissions.permissions import RolePermission
from permissions.filters import RoleFilterBackend


class RetrieveListUpdateViewSet(mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides default `retrieve()`, `update()`,
    `partial_update()`,  and `list()` actions.
    with RolePermission
    """


class CreateRetrieveListUpdateViewSet(mixins.CreateModelMixin,
                                      mixins.RetrieveModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.ListModelMixin,
                                      viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`， `retrieve()`, `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass


class CreateRetrieveListViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`， `retrieve()`, `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass


class CreateRetrieveUpdateViewSet(mixins.CreateModelMixin,
                                  mixins.RetrieveModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`， `retrieve()`, `update()`,
    `partial_update()`  actions.
    """
    pass


class UpdateViewSet(
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    """
    A viewset that provides default  `update()`,
    `partial_update()` actions.
    """
    pass


class CreateViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`， `retrieve()`, `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass


class ListUpdateViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides default  `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides default  `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass


class RoleFilterMixViewSet():

    roles_filterbackends = []
    filter_backends = [RoleFilterBackend]

    def get_roles_filterbackends(self):
        return [filterbackend for filterbackend in self.roles_filterbackends]
