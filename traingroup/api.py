from distutils.util import strtobool

import rest_framework_filters as filters
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from common.viewset import CreateRetrieveListUpdateViewSet, ListUpdateViewSet
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseNotFound
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from permissions.filters import RoleFilterBackend, BOOLEAN_CHOICES, WhlRestFilterBackend
from permissions.permissions import RolePermission
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers import UserDetailsSerializer

from .filter import IsManagerFilterBackend, IsOwnerFilterBackend
from .models import TrainGroup
from .serializers import (
    TrainGropListSerializer,
    TrainGropMemberListSerializer,
    TrainGroupModifySerializer,
    TrainGroupSerializer
)


class TrainGroupViewSet(CreateRetrieveListUpdateViewSet):
    """
    This viewset automatically provides `create`, `list`,`put:mobify`,`patch: mobify` ,`bulkdeleteand group` and \
        `detail` actions.
    """
    renderer_classes = (EmberJSONRenderer,)
    pagination_class = ListPagination
    queryset = TrainGroup.objects.all()
    serializer_class = TrainGroupSerializer
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerFilterBackend, IsOwnerFilterBackend]
    filter_backends = [RoleFilterBackend, WhlRestFilterBackend]

    # def get_queryset(self):
    #     user = self.request.user
    #     return TrainGroup.objects.filter(administrator=user)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return TrainGropListSerializer
        if self.request.method == 'PUT':
            return TrainGroupModifySerializer

        return TrainGroupSerializer

    # def create(self, request, *args, **kwargs):
    #     """

    #     创建群组
    #     """
    #     data = request.data
    #     serializer = self.get_serializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     # response_data = {'status': 'ok', 'data': serializer.data}
    #     return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    @action(detail=False, methods=['PATCH'])
    def bulkdelete(self, request, *args, **kwargs):
        """
        批量删除群组

        """
        renderer_classes = (EmberJSONRenderer,)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.delettraingrouplist()

        return Response({})

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}

    #     return Response(serializer.data)


# exclude_param = openapi.Parameter('exclude',
#                                   in_=openapi.IN_QUERY,
#                                   description='不属于这个组的用户',
#                                   type=openapi.TYPE_BOOLEAN)


# @method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[exclude_param]))

class TrainGropMemberFilterSet(filters.FilterSet):
    exclude = filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES,
                                        coerce=strtobool, method='filter_exclude')

    def __init__(self, data=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
        # if filterset is bound, use initial values as defaults
        if data is not None:
            # get a mutable copy of the QueryDict
            data = data.copy()

            # filter param is either missing or empty, use initial as default
            if not data.get('exclude'):
                data['exclude'] = 'false'

        super(TrainGropMemberFilterSet, self).__init__(data, *args, **kwargs)

    def filter_exclude(self, queryset, name, value):
        groupid = self.view_kwargs.get('groupid', None)
        if value:
            return queryset.exclude(istrainofgroups__id=groupid)
        else:
            return queryset.filter(istrainofgroups__id=groupid)


class TrainGropMemberModifyViewSet(ListUpdateViewSet):
    """
    获取群组成员支持分页
    PUT:增加群组成员
    PATCH：删除群组成员
    """
    User = get_user_model()
    renderer_classes = (EmberJSONRenderer,)
    queryset = User.objects.all()
    pagination_class = ListPagination
    serializer_class = TrainGropMemberListSerializer
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerFilterBackend]
    filter_backends = [RoleFilterBackend, WhlRestFilterBackend]
    lookup_url_kwarg = 'groupid'
    filterset_class = TrainGropMemberFilterSet
    # def get_queryset(self):
    #     user = self.request.user
    #     return TrainGroup.objects.filter(administrator=user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailsSerializer
        else:
            return TrainGropMemberListSerializer

    # def get_object(self):
    #     groupid = self.kwargs.get('groupid', None)
    #     user = self.request.user
    #     traingroup = TrainGroup.objects.get(id=groupid)
    #     if traingroup.administrator.id != user.id:
    #         raise Http404('you not allow to query this group.')
    #     return traingroup
    def get_queryset(self):
        if self.action == 'list':
            User = get_user_model()
            return User.objects.all()
        return super().get_queryset()

    # def get_queryset(self):

    #     if self.action == 'list':
    #         groupid = self.kwargs.get('groupid', None)
    #         user = self.request.user
    #         # traingroup = TrainGroup.objects.get(id=groupid)
    #         # exclude = self.request.query_params.get('exclude', 'false')

    #         # if strtobool(exclude):
    #         #     return querySet.objects.exclude(istrainofgroups__id=groupid)
    #         # else:
    #         #     return User.filter(istrainofgroups__id=groupid)

    #         # User.objects.filter(department__slug__startswith=slug).exclude(istrainofgroups__id=groupid)
    #         #     # return User.objects.exclude(istrainofgroups__id=groupid)            else:
    #         #     return traingroup.trainers.all()
    #         User.objects.filter()

    #         raise Http404('this user not manager  department.')
    #         except TrainGroup.DoesNotExist as e:
    #             raise Http404('No traingroup matches the given query.')
    #     else:
    #         return queryset

    # def list(self, request, *args, **kwargs):
    #     """
    #     获取群组成员支持分页
    #     """
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    # def update(self, request, *args, **kwargs):
    #     """
    #     PUT:增加群组成员
    #     PATCH：删除群组成员

    #     """

    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}
    #     return Response({'status': 'ok'})


# class TrainManagerViewSet(viewsets.ModelViewSet):
#     """
#     This viewset automatically provides `list` and `detail` actions.
#     """
#     renderer_classes = (EmberJSONRenderer,)
#     queryset = TrainManagerPermission.objects.all()
#     serializer_class = TrainManagerPermissionSerializer
