# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError

from rest_framework import serializers  # , exceptions
from traingroup.models import TrainGroup
from .models import LearnPlan, LearnProgress
from course.serializers import CoursewareSerializer, CoursewareReadonlySerializer
from common.selffield import ChoiceField
import pendulum

from django.utils import timezone


class LearnPlanSerializer(serializers.ModelSerializer):

    traingroups = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=TrainGroup.objects.all())
    creater = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    status = ChoiceField(required=False, choices=LearnPlan.STATUS_CHOICES)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = LearnPlan
        fields = ['id', 'name', 'start_time', 'course', 'course_name',
                  'creater', 'end_time', 'orexame', 'traingroups', 'status']
        read_only_fields = ('id', 'create_time', 'creater', 'course_name', 'status')
        ordering = ['create_time']
        extra_kwargs = {'traingroups': {'write_only': True}, 'course': {'write_only': True}}

    def create(self, validated_data):
        traingroups = validated_data['traingroups']
        instance = super(LearnPlanSerializer, self).create(validated_data)
        for traingroup in traingroups:
            trainers = traingroup.get_trainers()
            if trainers:
                for trainer in trainers:
                    trainer.learnplan_progresses.create(plan_no=instance, traingroup=traingroup)
        return instance


class LearnPlanReadonlySerializer(serializers.ModelSerializer):
    course = CoursewareReadonlySerializer()
    ratio = serializers.SerializerMethodField()
    questionanswer = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = LearnPlan
        fields = ['id', 'name', 'start_time', 'creater', 'questionanswer',
                  'course', 'ratio', 'end_time', 'orexame', 'status']
        read_only_fields = ('id', 'name', 'start_time', 'creater', 'questionanswer',
                            'course', 'ratio', 'end_time', 'orexame', 'status')
        ordering = ['create_time']

    def get_questionanswer(self, learnplan):
        num_completed = learnplan.plan_progresses.filter(status='completed').count()
        count = learnplan.plan_progresses.count()
        return '{}/{}'.format(num_completed, count)

    def get_ratio(self, learnplan):
        num_completed = learnplan.plan_progresses.filter(status='completed').count()
        count = learnplan.plan_progresses.count()
        return '{}/{}'.format(num_completed, count)


class LearnPlanGroupSerializer(serializers.ModelSerializer):
    traingroup = serializers.PrimaryKeyRelatedField(required=False, many=True, read_only=True)

    class Meta:
        model = LearnPlan
        fields = ['traingroup']
        read_only_fields = ['traingroup']
        ordering = ['create_time']


class LearnProgressSerializer(serializers.ModelSerializer):
    #course = CoursewareReadonlySerializer(source='plan_no.course')
    plan = LearnPlanReadonlySerializer(source='plan_no')
    status = ChoiceField(choices=LearnProgress.STATUS_CHOICES)

    class Meta:
        model = LearnProgress
        fields = '__all__'
        read_only_fields = ('plan', 'type', 'create_time', 'trainer', 'course', 'plan')
        ordering = ['create_time']

    def to_internal_value(self, data):
        if self.instance.status == 'completed' or self.instance.status == 'overdueCompleted':
            data.pop('status', None)
        if self.instance.status == 'learning':
            status = data.get('status', 'learning')
            if status == 'completed' or status == 'overdueCompleted':
                data['end_time'] = timezone.now()
                if data['end_time'] > self.instance.plan_no.end_time:
                    data['status'] = 'overdueCompleted'
        ret = super(LearnProgressSerializer, self).to_internal_value(data)
        # 修改修改学习计划的状态

        return ret


class LearnProgressByGroupSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.name')
    trainer_no = serializers.CharField(source='trainer.user_no')
    trainer_department = serializers.CharField(source='trainer.department.name')
    #status = ChoiceField(choices=LearnProgress.STATUS_CHOICES)
    status = serializers.SerializerMethodField()
    learnqusratio = serializers.SerializerMethodField()

    def get_learnqusratio(self, learnprogress):
        questions_count = learnprogress.questions.count()
        questions_answercount = learnprogress.questions.filter(unanswer=True).count()
        return '{}/{}'.format(questions_answercount, questions_count)

    class Meta:
        model = LearnProgress
        fields = ['trainer_name', 'trainer_no', 'trainer_department', 'status', 'learnqusratio']
        read_only_fields = ('trainer_name', 'trainer_no', 'trainer_department', 'status', 'learnqusratio')
        ordering = ['create_time']

    def get_status(self, learnprogress):
        today = pendulum.today().date()
        period = pendulum.period(today, learnprogress.plan_no.start_time)
        if learnprogress.status == 'assigned' and period.remaining_days > 0:
            return '已指派'
        else:
            return learnprogress.get_status_display()


class LearnProgressOnlySerializer(serializers.ModelSerializer):
    #course = CoursewareReadonlySerializer(source='plan_no.course')
    plan = LearnPlanReadonlySerializer(source='plan_no')
    status = serializers.SerializerMethodField()
    rate_progress = serializers.SerializerMethodField()

    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = LearnProgress
        fields = ['id', 'plan', 'type', 'rate_progress', 'progress', 'days_remaining', 'status', 'create_time']
        read_only_fields = ('id', 'plan', 'type', 'rate_progress', 'progress',
                            'days_remaining', 'status', 'create_time')
        ordering = ['create_time']

    def get_rate_progress(self, learnprogress):
        property = learnprogress.plan_no.course.property

        if learnprogress.plan_no.course.file_type == 'PDF':
            numpage = learnprogress.progress['numpage']
            return round(100*numpage/property['numpages'])

        if learnprogress.plan_no.course.file_type == 'MP4':
            starttime = learnprogress.progress.get('starttime', 0)
            return round(100*starttime/property['duration'])

    def get_days_remaining(self, learnprogress):
        today = pendulum.today().date()
        period = pendulum.period(learnprogress.plan_no.end_time, today, absolute=True)
        return period.days

    def get_status(self, learnprogress):
        today = pendulum.today().date()
        period = pendulum.period(today, learnprogress.plan_no.start_time)
        if learnprogress.status == 'assigned' and period.remaining_days > 0:
            return '未开始'
        else:
            return learnprogress.get_status_display()


class AggregationSetForEmployee(serializers.Serializer):
    learncompletedes = LearnProgressOnlySerializer(many=True)
    learntodoes = LearnProgressOnlySerializer(many=True)
    learnoverdue = LearnProgressOnlySerializer(many=True)

    class Meta:

        fields = '__all__'
        read_only_fields = ('learncompletedes', 'learntodoes', 'learnoverdue')
