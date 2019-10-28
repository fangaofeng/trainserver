from rest_framework import mixins, views
from rest_framework import viewsets


class RetrieveListUpdateViewSet(mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides default `retrieve()`, `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass


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


class CreateRetrieveUpdateViewSet(mixins.CreateModelMixin,
                                  mixins.RetrieveModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`， `retrieve()`, `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass


class ListUpdateViewSet(viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`， `retrieve()`, `update()`,
    `partial_update()`,  and `list()` actions.
    """
    pass
