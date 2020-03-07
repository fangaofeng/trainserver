# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError

from rest_framework import serializers  # , exceptions
from traingroup.models import TrainGroup
from exampaper.serializers import ExamPaPerSerializer
from .models import ExamPlan, ExamProgress
from common.selffield import ChoiceField
import pendulum
from django.utils import timezone
from rest_flex_fields import FlexFieldsModelSerializer
from common.serializers import OwnerFlexFSerializer, OwnerFieldSerializer, CurrentUserDepartmentDefault


class ExamPlanSerializer(OwnerFlexFSerializer):
    department = serializers.HiddenField(
        default=CurrentUserDepartmentDefault()
    )
    status = ChoiceField(required=False, choices=ExamPlan.STATUS_CHOICES)
    ratio = serializers.SerializerMethodField()

    class Meta:
        model = ExamPlan
        fields = ['id', 'name', 'start_time', 'exampaper', 'department',
                  'creater', 'end_time', 'traingroups', 'status', 'ratio']
        read_only_fields = ('id', 'created', 'creater', 'status', 'ratio')
        ordering = ['created']
        extra_kwargs = {'traingroups': {'write_only': True}, 'course': {'write_only': True}}
        expandable_fields = {'exampaper': ExamPaPerSerializer}

    def get_ratio(self, examplan):
        num_completed = examplan.progresses.filter(status='completed').count()
        count = examplan.progresses.count()
        return '{}/{}'.format(num_completed, count)

    def create(self, validated_data):
        traingroups = validated_data['traingroups']
        instance = super(ExamPlanSerializer, self).create(validated_data)
        quesitons = instance.exampaper.get_quesitons()
        for traingroup in traingroups:
            trainers = traingroup.get_trainers()
            if trainers:
                for trainer in trainers:
                    # 添加 answers
                    answers = instance.exampaper.get_quesitons()
                    answerlist = list(answers)
                    for value in answerlist:
                        value.update(answer='')
                    trainer.examplan_progresses.create(plan=instance, answers=answerlist)
        return instance


class ExamPlanReadonlySerializer(OwnerFlexFSerializer):
    exampaper = ExamPaPerSerializer()
    ratio = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = ExamPlan
        fields = ['id', 'name', 'start_time', 'creater',
                  'exampaper', 'ratio', 'end_time',  'status']
        read_only_fields = ('id', 'name', 'start_time', 'creater',
                            'exampaper', 'ratio', 'end_time', 'status')
        ordering = ['created']
        expandable_fields = {'exampaper': ExamPaPerSerializer}

    def get_ratio(self, examplan):
        num_completed = examplan.progresses.filter(status='completed').count()
        count = examplan.progresses.count()
        return '{}/{}'.format(num_completed, count)


class ExamPlanGroupSerializer(serializers.ModelSerializer):
    traingroup = serializers.PrimaryKeyRelatedField(required=False, many=True, read_only=True)

    class Meta:
        model = ExamPlan
        fields = ['traingroup']
        read_only_fields = ['traingroup']
        ordering = ['created']


class ExamProgressSerializer(OwnerFlexFSerializer):

    status = ChoiceField(choices=ExamProgress.STATUS_CHOICES)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = ExamProgress
        fields = ['id', 'created', 'trainer', 'plan', 'status',
                  'start_time', 'end_time', 'score', 'answers', 'days_remaining']
        read_only_fields = ('id', 'created', 'trainer', 'plan', 'score',  'days_remaining')
        ordering = ['created']
        expandable_fields = {'plan': ExamPlanReadonlySerializer}

    def get_days_remaining(self, examprogress):
        today = pendulum.today().date()
        period = pendulum.period(today, examprogress.plan.end_time.date(),  absolute=False)
        return period.days if period.days > 0 else 0


class ExamProgressModifySerializer(OwnerFieldSerializer):

    status = ChoiceField(choices=ExamProgress.STATUS_CHOICES)

    class Meta:
        model = ExamProgress
        fields = ['id', 'answers', 'score', 'status']
        read_only_fields = ['status']

    def to_internal_value(self, data):
        if self.instance.status == 'completed' or self.instance.status == 'overdueCompleted':
            data.pop('status', None)
        if self.instance.status == 'examing':
            status = data.get('status', 'examing')
            if status == 'completed' or status == 'overdueCompleted':
                data['end_time'] = timezone.now()
                if data['end_time'] > self.instance.plan.end_time:
                    data['status'] = 'overdueCompleted'
        cerect_answer = self.instance.plan.exampaper.questions.all().values('id', 'answer', 'score')
        answers = data.get('answers', None)
        cerect_answerdict = {}
        score = 0
        for item in cerect_answer:
            id = item['id']
            cerect_answerdict.update({id: {'answer': item['answer'], 'score': item['score']}})
        for answer in answers:
            id = answer['id']

            if answer['answer'] == cerect_answerdict[id]['answer']:
                score += cerect_answerdict[id]['score']
        if self.instance.score >= score:
            data.pop('answers', None)
        else:
            data.update(score=score)

        ret = super(ExamProgressModifySerializer, self).to_internal_value(data)
        # 修改考试的状态

        return ret


class ExamProgressByGroupSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.name')
    trainer_no = serializers.CharField(source='trainer.user_no')
    trainer_department = serializers.CharField(source='trainer.department.name')
    status = ChoiceField(choices=ExamProgress.STATUS_CHOICES)

    class Meta:
        model = ExamProgress
        fields = ['trainer_name', 'trainer_no', 'trainer_department', 'status']
        read_only_fields = ('trainer_name', 'trainer_no', 'trainer_department', 'status')
        ordering = ['created']

    def to_internal_value(self):
        super(ExamProgressByGroupSerializer, self).to_internal_value()


class ExamProgressOnlySerializer(serializers.ModelSerializer):
    plan = ExamPlanReadonlySerializer()
    status = ChoiceField(choices=ExamProgress.STATUS_CHOICES)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = ExamProgress
        fields = ['id', 'created', 'trainer', 'plan', 'status', 'start_time',
                  'end_time', 'score', 'answers', 'days_remaining']
        read_only_fields = ['id', 'created', 'trainer', 'plan',
                            'status', 'start_time', 'score', 'answers', 'days_remaining']
        ordering = ['created']

    def get_days_remaining(self, examprogress):
        today = pendulum.today().date()
        period = pendulum.period(examprogress.plan.end_time.date(), today, absolute=True)
        return period.days


class ExamAggregationForEmployee(serializers.Serializer):
    completed = ExamProgressOnlySerializer(many=True)
    todo = ExamProgressOnlySerializer(many=True)
    overdue = ExamProgressOnlySerializer(many=True)

    class Meta:

        fields = '__all__'
        read_only_fields = ('completed', 'todo', 'overdue')
