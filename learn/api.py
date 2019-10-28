from rest_framework import viewsets, generics
from django.db.models import Q

from .models import LearnPlan, LearnProgress
from .serializers import LearnPlanSerializer, LearnProgressSerializer, LearnProgressOnlySerializer, LearnProgressByGroupSerializer, LearnPlanReadonlySerializer, AggregationSetForEmployee
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from django.contrib.auth import get_user_model
from users.serializers import UserDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from common.viewset import RetrieveListUpdateViewSet, CreateRetrieveListUpdateViewSet
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ModelChoiceFilter, ChoiceFilter
import rest_framework_filters as filters
from rest_framework_filters import backends
from traingroup.serializers import TrainGroupLearnPlanSerializer
from django.db.models import Q
import pendulum
from django.utils import timezone


class LearnPlanFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ('noarchiving', '不包含已归档'),
    ]
    STATUS_CHOICES.extend(list(LearnPlan.STATUS_CHOICES))
    status = ChoiceFilter(choices=STATUS_CHOICES, method='filter_status')

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
    permission_classes = (IsAuthenticated,)
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = LearnPlanFilter

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
    #queryset = LearnPlan.objects.all()
    serializer_class = TrainGroupLearnPlanSerializer
    pagination_class = ListPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        learnplanid = self.kwargs.get('learnplanid')
        user = self.request.user

        try:
            learnplan = LearnPlan.objects.get(id=learnplanid)
            if learnplan.creater.id != user.id:
                raise Http404('you not allow to query this group of learnplan.')
            return learnplan.traingroups.all()

        except learnplan.DoesNotExist as e:
            raise Http404('No traingroup matches the given learnplan query .')
        return []


class LearnPlanViewGroupMemberProgressSet(generics.ListAPIView):
    """
    This view automatically provides `list`  actions for group fo learnplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    #queryset = LearnPlan.objects.all()
    serializer_class = LearnProgressByGroupSerializer
    pagination_class = ListPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        learnplanid = self.kwargs.get('learnplanid')
        groupid = self.kwargs.get('groupid')
        user = self.request.user
        learnplan = LearnPlan.objects.get(id=learnplanid)
        if learnplan.creater.id != user.id:
            raise Http404('you not allow to query this group of learnplan.')
        if learnplan.creater.id != user.id:
            raise Http404('you not allow to query this group of learnplan.')
        try:
            return learnplan.plan_progresses.filter(traingroup=groupid).all()

        except learnplan.DoesNotExist as e:
            raise Http404('No traingroup matches the given learnplan query .')
        return []


class progressFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ('notcompleted', '学习中'),
        ('completed', '已完成'),
        ('overdue', '已逾期'),
    ]
    # STATUS_CHOICES.extend(list(LearnProgress.STATUS_CHOICES))
    status = ChoiceFilter(choices=STATUS_CHOICES, method='filter_status')

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
    permission_classes = (IsAuthenticated,)
    filter_backends = (backends.RestFrameworkFilterBackend, )
    # filter_backends = (DjangoFilterBackend,)
    filterset_class = progressFilter

    def get_object(self):

        learnprogress = super(LearnProgressViewSet, self).get_object()
        return learnprogress

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return LearnProgressOnlySerializer
        return super(LearnProgressViewSet, self).get_serializer_class()

    def get_queryset(self):

        user = self.request.user
        queryset = LearnProgress.objects.filter(trainer=user).order_by('-create_time')
        return queryset

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


class LearnProgressViewAggregationSet(generics.RetrieveAPIView):
    """
    aggregation:返回员工的学习和考试分类聚合
    param： size ，每个分类返回的数量
    """

    renderer_classes = (EmberJSONRenderer,)

    serializer_class = AggregationSetForEmployee
    permission_classes = (IsAuthenticated,)

    def get_object(self):

        user = self.request.user
        learntodoes = LearnProgress.objects.filter(trainer=user).filter(
            Q(status='assigned') | Q(status='learning')).order_by('-create_time')[0:4]
        learncompletedes = LearnProgress.objects.filter(trainer=user).filter(
            Q(status='completed') | Q(status='overdueCompleted')).order_by('-create_time')[0:4]
        learnoverdue = LearnProgress.objects.filter(
            trainer=user, status='overdueNotCompleted').order_by('-create_time')[0:4]
        data = {
            'learncompletedes': learncompletedes,
            'learntodoes': learntodoes,
            'learnoverdue': learnoverdue
        }
        # data=[learntodoes]
        return data
