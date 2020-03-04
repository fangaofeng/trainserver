# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError
from rest_framework import serializers  # , exceptions
from .models import TrainGroup
from django.contrib.auth import get_user_model
from users.serializers import UserDetailsSerializer
from rest_framework.utils import model_meta
from rest_framework.serializers import raise_errors_on_nested_writes, CreateOnlyDefault
from common.serializers import CurrentUserDepartmentDefault


class TrainGroupSerializer(serializers.ModelSerializer):
    department = serializers.HiddenField(
        default=CurrentUserDepartmentDefault()
    )
    count = serializers.SerializerMethodField()

    class Meta:
        model = TrainGroup
        fields = ('id', 'created_time', 'trainers', 'group_no', 'department', 'name', 'count')
        read_only_fields = ('created_time', 'group_no', 'id', 'count')
        extra_kwargs = {'trainers': {'write_only': True}}
        ordering = ['created_time']

    def get_count(self, traingroup):
        return traingroup.trainers.count()

    def validate(self, attrs):
        return attrs

    def generateGroupNo(self, validated_data, instance):
        department = validated_data['department']
        return ''.join([str(department), str(instance.id).zfill(6)])

    def create(self, validated_data):
        #validated_data['administrator'] = self.initial_data['administrator']
        instance = super(TrainGroupSerializer, self).create(validated_data)
        instance.group_no = self.generateGroupNo(validated_data, instance)
        instance.save()
        return instance


class TrainGroupLearnPlanSerializer(serializers.ModelSerializer):
    #plan_no = serializers.IntegerField(required=True,write_only=True)
    count = serializers.SerializerMethodField()
    learnplanration = serializers.SerializerMethodField()
    learnqusratio = serializers.SerializerMethodField()

    class Meta:
        model = TrainGroup
        fields = ('id', 'created_time', 'group_no', 'name', 'count', 'learnplanration', 'learnqusratio')
        read_only_fields = ('id', 'created_time', 'group_no', 'name', 'count', 'learnplanration', 'learnqusratio')

        ordering = ['created_time']

    def get_count(self, traingroup):
        return traingroup.trainers.count()

    def get_learnplanration(self, traingroup):

        plan_no = self.context['view'].kwargs.get('learnplanid')
        train_count = traingroup.trainers.count()
        completed_count = traingroup.learnplan_progress.filter(plan_no=plan_no, status='completed').count()
        return '{}/{}'.format(completed_count, train_count)

    def get_learnqusratio(self, traingroup):
        return traingroup.trainers.count()


class TrainGroupExamPlanSerializer(serializers.ModelSerializer):

    count = serializers.SerializerMethodField()
    examplanration = serializers.SerializerMethodField()

    class Meta:
        model = TrainGroup
        fields = ('id', 'created_time', 'group_no', 'name', 'count', 'examplanration')
        read_only_fields = ('id', 'created_time', 'group_no', 'name', 'count', 'examplanration')

        ordering = ['created_time']

    def get_count(self, traingroup):
        return traingroup.trainers.count()

    def get_examplanration(self, traingroup):

        plan_id = self.context['view'].kwargs.get('planid')
        train_count = traingroup.trainers.count()
        completed_count = traingroup.examplan_progresses.filter(plan=plan_id, status='completed').count()
        return '{}/{}'.format(completed_count, train_count)


class TrainGroupModifySerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainGroup
        fields = ['name']


class TrainGropListSerializer(serializers.Serializer):

    traingroups = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=TrainGroup.objects.all())

    class Meta:
        fields = ['traingroups']

    def delettraingrouplist(self):
        for traingroup in self.validated_data['traingroups']:
            traingroup.delete()


class TrainGropMemberListSerializer(serializers.ModelSerializer):

    User = get_user_model()
    trainers = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=User.objects.all())

    class Meta:
        model = TrainGroup
        fields = ['trainers']
        ordering = ['created_time']
        depth = 1

    def add(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.add(*value)
            else:
                setattr(instance, attr, value)
        return instance.save()

    def remove(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.remove(*value)
            else:
                setattr(instance, attr, value)
        # instance.save()
        return instance

    def update(self, instance, validated_data):
        if self.partial:
            self.remove(instance, validated_data)
        else:
            self.add(instance, validated_data)

        return instance


# class TrainManagerPermissionSerializer(serializers.ModelSerializer):
#     """
#     Serializer for Token model.
#     """
#     User = get_user_model()
#     administrator = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects.filter(role=1))

#     class Meta:
#         model = TrainManagerPermission
#         fields = ('id', 'created_time', 'administrator', 'department')
#         read_only_fields = ('created_time',)
#         ordering = ['created_time']
