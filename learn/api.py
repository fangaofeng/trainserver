import pendulum

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import rest_framework_filters as filters
# from rest_framework_filters.backends import RestFrameworkFilterBackend
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from common.viewset import (CreateRetrieveListUpdateViewSet, CreateViewSet,
                            RetrieveListUpdateViewSet)
from permissions.permissions import RolePermission
from permissions.filters import RoleFilterBackend
from traingroup.serializers import TrainGroupLearnPlanSerializer
from users.serializers import UserDetailsSerializer

from .filter import IsManagerFilterBackend, IsManagerProgressFilterBackend, IsOwnerFilterBackend
from .models import LearnPlan, LearnProgress, PublicLearnProgress
from .serializers import (AggregationSetForEmployee,
                          LearnPlanReadonlySerializer, LearnPlanSerializer,
                          LearnProgressByGroupSerializer,
                          LearnProgressReadOnlySerializer,
                          LearnProgressSerializer,
                          PublicLearnProgressReadonlySerializer,
                          PublicLearnProgressSerializer)


class LearnPlanFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ('noarchiving', '不包含已归档'),
    ]
    STATUS_CHOICES.extend(list(LearnPlan.STATUS_CHOICES))
    status = filters.ChoiceFilter(choices=STATUS_CHOICES, method='filter_status')

    def filter_status(self, queryset, name, value):
        if value == 'noarchiving':
            return queryset.exclude(status='archiving')
        return queryset

    class Meta:
        model = LearnPlan
        fields = ['status']


class LearnPlanViewSet(CreateRetrieveListUpdateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    renderer_classes = (EmberJSONRenderer,)
    queryset = LearnPlan.objects.all()
    serializer_class = LearnPlanSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    filter_backends = [RoleFilterBackend]
    filterset_class = LearnPlanFilter
    roles_filterbackends = [IsManagerFilterBackend]

    def get_filter_backends(self):
        if self.action == 'list':
            return [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
        return super().get_filter_backends()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LearnPlanReadonlySerializer
        else:
            return LearnPlanSerializer


class LearnPlanViewGroupSet(generics.ListAPIView):
    """
    This view automatically provides `list`  actions for group fo learnplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    # queryset = LearnPlan.objects.all()
    serializer_class = TrainGroupLearnPlanSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerFilterBackend]
    filter_backends = [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]

    def get_queryset(self):
        learnplanid = self.kwargs.get('learnplanid')

        # LearnPlan.objects.filter(id=learnplanid)
        #    if learnplan.creater.id != user.id:
        #         raise Http404('you not allow to query this group of learnplan.')
        #     return learnplan.traingroups.all()

        # except learnplan.DoesNotExist as e:
        #     return []


class LearnProgressViewGroupMemberSet(generics.ListAPIView):
    """
      This view automatically provides `list`  actions for progress of the memeber of  the group fo the learnplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    # queryset = LearnPlan.objects.all()
    serializer_class = LearnProgressByGroupSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerProgressFilterBackend]
    filter_backends = [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]

    def get_queryset(self):
        planid = self.kwargs.get('planid')
        groupid = self.kwargs.get('groupid')
        return LearnProgress.objects.filter(plan_id=planid).filter(traingroup_id=groupid)


class progressFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ('notcompleted', '学习中'),
        ('completed', '已完成'),
        ('overdue', '已逾期'),
    ]
    # STATUS_CHOICES.extend(list(LearnProgress.STATUS_CHOICES))
    status = filters.ChoiceFilter(choices=STATUS_CHOICES, method='filter_status')

    def filter_status(self, queryset, name, value):
        if value == 'notcompleted':
            return queryset.filter(
                Q(status='learning') | Q(status='assigned')).order_by('-create_time')
        if value == 'completed':
            return queryset.filter(status='completed')
        if value == 'overdue':
            return queryset.filter(status='overdue')
        return queryset

    class Meta:
        model = LearnProgress
        fields = ['status']


class LearnProgressViewSet(RetrieveListUpdateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    renderer_classes = (EmberJSONRenderer,)
    queryset = LearnProgress.objects.all().order_by('-create_time')
    serializer_class = LearnProgressSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    filter_backends = [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
    filterset_class = progressFilter
    roles_filterbackends = [IsManagerProgressFilterBackend, IsOwnerFilterBackend]

    # filter_backends = (DjangoFilterBackend,)
    # def get_object(self):

    #     learnprogress = super(LearnProgressViewSet, self).get_object()
    #     return learnprogress

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return LearnProgressReadOnlySerializer
        return super().get_serializer_class()

    # def get_queryset(self):

    #     user = self.request.user
    #     queryset = LearnProgress.objects.filter(trainer=user).order_by('-create_time')
    #     return queryset

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        if instance.trainer.id == user.id and instance.status == 'assigned':
            instance.status = 'learning'
            # 判断时间修改为status超期

            instance.start_time = timezone.now()

            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        # status 需要特殊处理
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class PublicLearnProgressViewSet(CreateRetrieveListUpdateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    renderer_classes = (EmberJSONRenderer,)
    queryset = PublicLearnProgress.objects.all().order_by('-created')
    serializer_class = PublicLearnProgressSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    # filter_backends = (backends.RestFrameworkFilterBackend, )
    # # filter_backends = (DjangoFilterBackend,)
    # filterset_class = progressFilter

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return PublicLearnProgressReadonlySerializer

        return super(PublicLearnProgressViewSet, self).get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = PublicLearnProgress.objects.filter(creater=self.request.user).order_by('-created')
        else:
            queryset = PublicLearnProgress.objects.none()

        return queryset

    def create(self, request, *args, **kwargs):
        course = request.data.get('course', None)
        queryset = self.filter_queryset(self.get_queryset())

        try:
            instance = queryset.get(course__id=course)
            serializer = self.get_serializer(instance)
        except PublicLearnProgress.DoesNotExist as e:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=False)
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class LearnProgressViewAggregationSet(generics.RetrieveAPIView):
    """
    aggregation:返回学员的学习和考试分类聚合
    param： size ，每个分类返回的数量
    """

    renderer_classes = (EmberJSONRenderer,)

    serializer_class = AggregationSetForEmployee
    permission_classes = [RolePermission]

    def get_object(self):

        user = self.request.user
        queryset = LearnProgress.objects.filter(trainer=user)
        learntodoes = queryset.filter(
            Q(status='assigned') | Q(status='learning')).order_by('-create_time')[0:4]
        learncompletedes = queryset.filter(
            Q(status='completed') | Q(status='overdueCompleted')).order_by('-create_time')[0:4]
        learnoverdue = queryset.filter(
            status='overdueNotCompleted').order_by('-create_time')[0:4]
        data = {
            'learncompletedes': learncompletedes,
            'learntodoes': learntodoes,
            'learnoverdue': learnoverdue
        }
        return data
