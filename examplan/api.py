from rest_framework import viewsets, generics
from .models import ExamPlan, ExamProgress
from .serializers import ExamPlanSerializer, ExamProgressSerializer, ExamProgressModifySerializer, ExamProgressByGroupSerializer, ExamProgressOnlySerializer, ExamAggregationForEmployee
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from common.viewset import RetrieveListUpdateViewSet, CreateRetrieveListUpdateViewSet
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ModelChoiceFilter, ChoiceFilter
import rest_framework_filters as filters
from rest_framework_filters import backends
from traingroup.serializers import TrainGroupExamPlanSerializer
from users.serializers import UserDetailsSerializer
from exampaper.serializers import QuestionExamSerializer
from django.db.models import Q
import pendulum
from django.utils import timezone
from datetime import datetime, timedelta


class ExamPlanFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ('noarchiving', '不包含已归档'),
    ]
    STATUS_CHOICES.extend(list(ExamPlan.STATUS_CHOICES))
    status = ChoiceFilter(choices=STATUS_CHOICES, method='filter_status')

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
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExamPlanFilter

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return ExamPlan.objects.filter(creater=user)
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return ExamPlanSerializer
    #     else:
    #         return ExamPlanSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve':
            kwargs.update(expand='exampaper')
        return super(ExamPlanViewSet, self).get_serializer(*args, **kwargs)
    # def create(self, request, *args, **kwargs):
    #     super(ExamPlanViewSet, self).create(request, *args, **kwargs)


class ExamPlanViewGroupSet(generics.ListAPIView):
    """
    This view automatically provides `list`  actions for group fo Examplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    #queryset = ExamPlan.objects.all()
    serializer_class = TrainGroupExamPlanSerializer
    pagination_class = ListPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        planid = self.kwargs.get('planid')
        user = self.request.user

        try:
            examplan = ExamPlan.objects.get(id=planid)
            if examplan.creater.id != user.id:
                raise Http404('you not allow to query this group of Examplan.')
            return examplan.traingroups.all()

        except ExamPlan.DoesNotExist as e:
            raise Http404('No traingroup matches the given Examplan query .')
        return []


class ExamPlanViewGroupMemberProgressSet(generics.ListAPIView):
    """
    This view automatically provides `list`  actions for group fo Examplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    #queryset = ExamPlan.objects.all()
    serializer_class = ExamProgressByGroupSerializer
    pagination_class = ListPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        planid = self.kwargs.get('planid')
        groupid = self.kwargs.get('groupid')
        user = self.request.user

        try:
            examplan = ExamPlan.objects.get(id=planid)
            if examplan.creater.id != user.id:
                raise Http404('you not allow to query this group of Examplan.')
            if examplan.creater.id != user.id:
                raise Http404('you not allow to query this group of Examplan.')
            return examplan.plan_progresses.filter(traingroup=groupid).all()

        except ExamPlan.DoesNotExist as e:
            raise Http404('No traingroup matches the given Examplan query .')
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
    permission_classes = (IsAuthenticated,)
    filter_backends = (backends.RestFrameworkFilterBackend,)
    filterset_class = progressFilter

    def get_object(self):
        Examprogress = super(ExamProgressViewSet, self).get_object()
        return Examprogress

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

    def get_queryset(self):

        user = self.request.user
        queryset = ExamProgress.objects.filter(trainer=user).order_by('-created')
        return queryset

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        duration = instance.plan.exampaper.duration

        now = timezone.now()
        if now > instance.plan.end_time:
            if instance.status != 'completed':
                instance.status = 'overdue'
                instance.save()
            return Response({'status': 'overdue', 'reason': 'exam time is passed'})
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


class ExamProgressViewQuestionSet(generics.ListAPIView):
    """
    This view automatically provides `list`  actions for group fo Examplan.
    """
    renderer_classes = (EmberJSONRenderer,)
    #queryset = ExamPlan.objects.all()
    serializer_class = QuestionExamSerializer
    pagination_class = ListPagination
    permission_classes = (IsAuthenticated,)

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
    aggregation:返回员工的学习和考试分类聚合
    param： size ，每个分类返回的数量
    """

    renderer_classes = (EmberJSONRenderer,)
    serializer_class = ExamAggregationForEmployee
    permission_classes = (IsAuthenticated,)

    def get_object(self):

        user = self.request.user
        examtodoes = ExamProgress.objects.filter(trainer=user).filter(
            Q(status='assigned') | Q(status='examing')).order_by('-created')[0:4]
        examcompletedes = ExamProgress.objects.filter(trainer=user).filter(
            Q(status='completed') | Q(status='overdueCompleted')).order_by('-created')[0:4]
        examoverdue = ExamProgress.objects.filter(
            trainer=user, status='overdueNotCompleted').order_by('-created')[0:4]
        data = {
            'examcompletedes': examcompletedes,
            'examtodoes': examtodoes,
            'examoverdue': examoverdue
        }
        # data=[Examtodoes]
        return data
