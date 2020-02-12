from datetime import datetime, timedelta

import pendulum
import rest_framework_filters as filters
# from rest_framework_filters.backends import RestFrameworkFilterBackend
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from common.viewset import CreateRetrieveListUpdateViewSet, ListViewSet, RetrieveListUpdateViewSet
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from exampaper.serializers import QuestionExamSerializer
from permissions.filters import RoleFilterBackend
from permissions.permissions import RolePermission
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from traingroup.models import TrainGroup
from traingroup.serializers import TrainGroupExamPlanSerializer
from users.serializers import UserDetailsSerializer

from .filter import IsManagerFilterBackend, IsManagerProgressFilterBackend, IsOwnerFilterBackend
from .models import ExamPlan, ExamProgress
from .serializers import (
    ExamAggregationForEmployee,
    ExamPlanSerializer,
    ExamProgressByGroupSerializer,
    ExamProgressModifySerializer,
    ExamProgressOnlySerializer,
    ExamProgressSerializer
)


class ExamPlanFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ('noarchiving', '不包含已归档'),
    ]
    STATUS_CHOICES.extend(list(ExamPlan.STATUS_CHOICES))
    status = filters.ChoiceFilter(choices=STATUS_CHOICES, method='filter_status')

    def filter_status(self, queryset, name, value):
        if value == 'noarchiving':
            return queryset.exclude(status='archiving')
        return queryset

    class Meta:
        model = ExamPlan
        fields = ['status']


class ExamPlanViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    renderer_classes = (EmberJSONRenderer,)
    queryset = ExamPlan.objects.all()
    serializer_class = ExamPlanSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    filter_backends = [RoleFilterBackend]
    filterset_class = ExamPlanFilter
    roles_filterbackends = [IsManagerFilterBackend]

    # def get_queryset(self):
    #     """
    #     This view should return a list of all the purchases
    #     for the currently authenticated user.
    #     """
    #     user = self.request.user
    #     return ExamPlan.objects.filter(creater=user)
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return ExamPlanSerializer
    #     else:
    #         return ExamPlanSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve':
            kwargs.update(expand='exampaper')
        return super(ExamPlanViewSet, self).get_serializer(*args, **kwargs)

    def get_filter_backends(self):
        if self.action == 'list':
            return [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
        return super().get_filter_backends()
    # def create(self, request, *args, **kwargs):
    #     super(ExamPlanViewSet, self).create(request, *args, **kwargs)


class ExamPlanViewGroupSet(ListViewSet):
    """
    This view automatically provides `list`  actions for groups fo Examplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    # queryset = ExamPlan.objects.all()
    serializer_class = TrainGroupExamPlanSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerFilterBackend]
    filter_backends = [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
    # def get_filter_backends(self):
    #     if self.request.method == 'GET':
    #         return [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
    #     return super().get_filter_backends()

    def get_queryset(self):
        planid = self.kwargs.get('planid')
        return TrainGroup.objects.filter(learn_plans=planid)


class ExamProgressViewGroupMemberSet(ListViewSet):
    """
    This view automatically provides `list`  actions for progress of the memeber of  the group fo the Examplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    # queryset = ExamPlan.objects.all()
    serializer_class = ExamProgressByGroupSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerProgressFilterBackend]
    filter_backends = [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
    # def get_filter_backends(self):
    #     if self.request.method == 'GET':
    #         return [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
    #     return super().get_filter_backends()

    def get_queryset(self):
        planid = self.kwargs.get('planid')
        groupid = self.kwargs.get('groupid')
        return ExamProgress.objects.filter(plan_id=planid).filter(traingroup_id=groupid)


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
                Q(status='examing') | Q(status='assigned')).order_by('-created')
        if value == 'completed':
            return queryset.filter(status='completed').order_by('-created')
        if value == 'overdue':
            return queryset.filter(status='overdue').order_by('-created')
        return queryset

    class Meta:
        model = ExamProgress
        fields = ['status']


class ExamProgressViewSet(RetrieveListUpdateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    renderer_classes = (EmberJSONRenderer,)
    queryset = ExamProgress.objects.all().order_by('-created')
    serializer_class = ExamProgressSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    filter_backends = [RoleFilterBackend]
    filterset_class = progressFilter
    roles_filterbackends = [IsManagerFilterBackend, IsOwnerFilterBackend]

    def get_filter_backends(self):
        if self.action == 'list':
            return [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
        return super().get_filter_backends()

    # def get_object(self):
    #     Examprogress = super(ExamProgressViewSet, self).get_object()
    #     return Examprogress

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return ExamProgressModifySerializer
        if getattr(self, 'swagger_fake_view', False):  # 抑制swagger错误

            return ExamProgressSerializer
        return super(ExamProgressViewSet, self).get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list' or self.action == 'retrieve':
            kwargs.update(expand='plan')
            kwargs.update(fields=['id', 'created', 'trainer', 'plan', 'status',
                                  'start_time', 'end_time', 'score', 'days_remaining'])
        return super(ExamProgressViewSet, self).get_serializer(*args, **kwargs)

    # def get_queryset(self):

    #     user = self.request.user
    #     queryset = ExamProgress.objects.filter(trainer=user).order_by('-created')
    #     return queryset

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        duration = instance.plan.exampaper.duration

        now = timezone.now()
        if now > instance.plan.end_time:
            if instance.status != 'completed':
                instance.status = 'overdue'
                instance.save()
            return Response({'status': 'overdue', 'reason': 'exam time is passed', "NOCHANGE": True})
        elif instance.status == 'assigned':
            instance.start_time = now
            instance.status = 'examing'
            now_d = now + timedelta(minutes=duration)
            if now_d > instance.plan.end_time:

                instance.end_time = instance.plan.end_time
            else:
                instance.end_time = now_d
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        now = timezone.now()
        now_d = now + timedelta(minutes=3)
        if now_d > instance.plan.end_time:
            return Response({'status': 'error', 'reason': 'exam time is passed'})

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        # status 需要特殊处理
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ExamProgressViewQuestionSet(ListViewSet):
    """
    This view automatically provides `list`  actions for group fo Examplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    # queryset = ExamPlan.objects.all()
    serializer_class = QuestionExamSerializer
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    filter_backends = [RoleFilterBackend]
    roles_filterbackends = [IsManagerFilterBackend, IsOwnerFilterBackend]

    # def get_filter_backends(self):
    #     if self.action == 'list':
    #         return [RoleFilterBackend]
    #     return super().get_filter_backends()

    def get_queryset(self):
        progressid = self.kwargs.get('progressid')
        user = self.request.user

        try:
            examprogress = ExamProgress.objects.get(id=progressid)
            if examprogress.trainer.id != user.id:
                raise Http404('you not allow to query this group of Examplan.')
            return examprogress.plan.exampaper.questions.all()

        except ExamPlan.DoesNotExist as e:
            raise Http404('No traingroup matches the given Examplan query .')
        return []


class ExamProgressViewAggregationSet(generics.RetrieveAPIView):
    """
    aggregation:返回学员的学习和考试分类聚合
    param： size ，每个分类返回的数量
    """

    renderer_classes = (EmberJSONRenderer,)
    serializer_class = ExamAggregationForEmployee
    permission_classes = [RolePermission]
    # roles_filterbackends = [iIsOwnerFilterBackends]
    # filter_backends = [RoleFilterBackend]
    # def get_filter_backends(self):
    #     if self.action == 'list':
    #         return [RoleFilterBackend]
    #     return super().get_filter_backends()

    def get_object(self):

        user = self.request.user
        queryset = ExamProgress.objects.filter(trainer=user)
        examtodoes = queryset.filter(
            Q(status='assigned') | Q(status='examing')).order_by('-created')[0:4]
        examcompletedes = queryset.filter(
            Q(status='completed') | Q(status='overdueCompleted')).order_by('-created')[0:4]
        examoverdue = queryset.filter(status='overdueNotCompleted').order_by('-created')[0:4]
        data = {
            'examcompletedes': examcompletedes,
            'examtodoes': examtodoes,
            'examoverdue': examoverdue
        }

        return data
