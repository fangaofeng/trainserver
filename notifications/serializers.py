# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers  # , exceptions

from common.selffield import ChoiceField
from orgs.serializers import DepartmentSerializer
from traingroup.models import TrainGroup

from .models import Notification, NotificationTask

UserModel = get_user_model()


class NUserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    department_name = serializers.ReadOnlyField(source='department.slug')
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = UserModel
        fields = ('id',  'name', 'avatar', 'user_no',
                  'employee_position',  'thumbnail', 'department_name')
        read_only_fields = ('name', 'employee_position', 'user_no', 'department_name')


class GenericNotificationRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, UserModel):
            serializer = NUserDetailsSerializer(value)

        return serializer.data


class NotificationTaskSerializer(FlexFieldsModelSerializer):
    # actor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    actor = GenericNotificationRelatedField(read_only=True)
    action = GenericNotificationRelatedField(read_only=True)
    target = GenericNotificationRelatedField(read_only=True)

    class Meta:
        model = NotificationTask
        fields = ('id', 'level', 'reason', 'actor',
                  'verb', 'description', 'target',
                  'action', 'public',
                  'data', 'users', 'departments', 'groups', )
        read_only_fields = ('id', 'actor', 'target', 'action', )
        ordering = ['created']


class NotificationListTaskSerializer(FlexFieldsModelSerializer):
    # actor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    actor = GenericNotificationRelatedField(read_only=True)
    action = GenericNotificationRelatedField(read_only=True)
    target = GenericNotificationRelatedField(read_only=True)

    class Meta:
        model = NotificationTask
        fields = ('id', 'level', 'reason', 'actor',
                  'verb', 'description', 'target',
                  'action', 'public',
                  'data', )
        read_only_fields = ('id', 'actor', 'target', 'action', )
        ordering = ['created']


class NotificationTaskCreateSerializer(serializers.ModelSerializer):
    actor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # actor = GenericNotificationRelatedField(read_only=True)
    action = GenericNotificationRelatedField(read_only=True)
    target = GenericNotificationRelatedField(read_only=True)

    class Meta:
        model = NotificationTask
        fields = ('id', 'level',  'reason', 'actor',
                  'verb', 'description', 'target',
                  'action', 'public',
                  'data', 'users', 'departments', 'groups')
        read_only_fields = ('id', 'actor', 'target', 'action', )
        ordering = ['created']
        extra_kwargs = {
            'groups': {'write_only': True},
            'departments': {'write_only': True},
            'users': {'write_only': True}}

    # def create(self, validated_data):
    #     instance = super().create(validated_data)
    #     users = cleaned_data.get('users', None)
    #     if users:
    #         recipient_users = users.distinct()
    #     else:
    #         recipient_users = User.objects.none()
    #     departments = cleaned_data.get('departments', None)
    #     if departments:
    #         recipient_users_departments = User.objects.filter(department__id__in=departments.all()).distinct()
    #     else:
    #         recipient_users_departments = User.objects.none()
    #     groups = cleaned_data.get('groups', None)
    #     if groups:
    #         recipient_user_groups = User.objects.filter(istrainofgroups__id__in=groups.all()).distinct()
    #     else:
    #         recipient_user_groups = User.objects.none()
    #     return instance


# class recipientsSerializers(serializers.PrimaryKeyRelatedField):
#     def get_queryset(self):
#         request = self.context.get('request', None)
#         queryset = super(recipientsSerializers, self).get_queryset()
#         if not request:
#             return None
#         user = request.user
#         return queryset.filter(deparment=user.managerdepartment)


# class trainergroupsSerializers(serializers.PrimaryKeyRelatedField):
#     def get_queryset(self):
#         request = self.context.get('request', None)
#         queryset = super(recipientsSerializers, self).get_queryset()
#         if not request:
#             return None
#         user = request.user
#         return queryset.filter(administrator=user)


# class NotificationCreateSerializer(serializers.ModelSerializer):

#     sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     recipients = NotificationTaskSerializer()

#     class Meta:
#         model = Notification
#         fields = ('level', 'recipients', 'trainergroups', 'sender',
#                   'verb', 'description', 'target',
#                   'action', 'public',
#                   'data')


class NotificationSerializer(serializers.ModelSerializer):

    # recipient = NUserDetailsSerializer()
    task = NotificationListTaskSerializer()

    class Meta:
        model = Notification
        fields = ('id', 'task', 'unread', 'emailed', 'created')
        read_only_fields = ('id', 'task', 'emailed', 'created')
