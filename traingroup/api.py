from rest_framework import viewsets, generics
from .models import TrainGroup, TrainManagerPermission
from .serializers import TrainGroupSerializer, TrainGroupModifySerializer, TrainGropListSerializer, TrainManagerPermissionSerializer, TrainGropMemberListSerializer
from common.pagination import ListPagination
from common.jsonrender import EmberJSONRenderer
from django.contrib.auth import get_user_model
from users.serializers import UserDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import Http404, HttpResponseNotFound
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from common.viewset import CreateRetrieveListUpdateViewSet


class TrainGroupViewSet(CreateRetrieveListUpdateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    renderer_classes = (EmberJSONRenderer,)
    pagination_class = ListPagination
    queryset = TrainGroup.objects.all()
    serializer_class = TrainGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return TrainGroup.objects.filter(administrator=user)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return TrainGropListSerializer
        if self.request.method == 'PUT':
            return TrainGroupModifySerializer

        return TrainGroupSerializer

    def create(self, request, *args, **kwargs):
        """

        创建群组
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = {'status': 'ok', 'data': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK, headers=headers)

    @action(detail=False, methods=['patch'])
    def bulkdelete(self, request, *args, **kwargs):
        """
        批量删除群组

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.delettraingrouplist()

        return Response({'status': 'ok'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response({'status': 'ok', 'data': serializer.data})


exclude_param = openapi.Parameter('exclude',
                                  in_=openapi.IN_QUERY,
                                  description='不属于这个组的用户',
                                  type=openapi.TYPE_BOOLEAN)


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[exclude_param]))
class TrainGropMemberModifyViewSet(viewsets.ModelViewSet):
    """
    获取群组成员支持分页
    PUT:增加群组成员
    PATCH：删除群组成员
    """
    renderer_classes = (EmberJSONRenderer,)
    queryset = TrainGroup.objects.all()
    pagination_class = ListPagination
    serializer_class = TrainGropMemberListSerializer
    permission_classes = (IsAuthenticated,)
    # def get_queryset(self):
    #     user = self.request.user
    #     return TrainGroup.objects.filter(administrator=user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailsSerializer
        else:
            return TrainGropMemberListSerializer

    def get_object(self):
        groupid = self.kwargs.get('groupid', None)
        user = self.request.user
        traingroup = TrainGroup.objects.get(id=groupid)
        if traingroup.administrator.id != user.id:
            raise Http404('you not allow to query this group.')
        return traingroup

    def get_queryset(self):
        groupid = self.kwargs.get('groupid', None)
        user = self.request.user
        traingroup = TrainGroup.objects.get(id=groupid)
        if traingroup.administrator.id != user.id:
            raise Http404('you not allow to query this group.')

        exclude = self.request.query_params.get('exclude', False)
        try:
            if exclude == 'true':
                User = get_user_model()
                slug = user.managerdepartment.department.slug
                return User.objects.filter(department__slug__startswith=slug).exclude(istrainofgroups__id=groupid)
                # return User.objects.exclude(istrainofgroups__id=groupid)
            else:
                return traingroup.trainers.all()
        except User.managerdepartment.RelatedObjectDoesNotExist as e:

            raise Http404('this user not manager  department.')
        except TrainGroup.DoesNotExist as e:
            raise Http404('No traingroup matches the given query.')

    def list(self, request, *args, **kwargs):
        """
        获取群组成员支持分页
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        PUT:增加群组成员
        PATCH：删除群组成员

        """

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response({'status': 'ok'})


class TrainManagerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    renderer_classes = (EmberJSONRenderer,)
    queryset = TrainManagerPermission.objects.all()
    serializer_class = TrainManagerPermissionSerializer
