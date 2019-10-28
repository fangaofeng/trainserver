# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError

from rest_framework import serializers  # , exceptions

from .models import Notification
from django.contrib.auth import get_user_model
from traingroup.models import TrainGroup
from common.selffield import ChoiceField
UserModel = get_user_model()


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    department_name = serializers.ReadOnlyField(source='department.slug')
    role_display = ChoiceField(source='role', choices=UserModel.EMPLOYEE_ROLE_CHOICES, required=False)

    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = UserModel
        fields = (
            'id', 'username', 'name', 'avatar', 'user_no', 'employee_position', 'role_display', 'thumbnail', 'department_name')
        read_only_fields = ('username', 'role', 'role_display', 'employee_position', 'user_no', 'department_name')


class GenericNotificationRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, UserModel):
            serializer = UserDetailsSerializer(value)

        return serializer.data


class NotificationSerializer(serializers.ModelSerializer):
    actor = GenericNotificationRelatedField(read_only=True)
    action_object = GenericNotificationRelatedField(read_only=True)
    target = GenericNotificationRelatedField(read_only=True)
    title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'level', 'recipient', 'title', 'unread', 'actor',
                  'verb', 'description', 'target',
                  'action_object', 'timestamp', 'public',
                  'data')
        read_only_fields = ('level',  'public', 'title')
        ordering = ['timestamp']

    def get_title(self, instance):
        return str(instance)


class recipientsSerializers(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(recipientsSerializers, self).get_queryset()
        if not request:
            return None
        user = request.user
        return queryset.filter(deparment=user.managerdepartment)


class trainergroupsSerializers(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        queryset = super(recipientsSerializers, self).get_queryset()
        if not request:
            return None
        user = request.user
        return queryset.filter(administrator=user)


class NotificationCreateSerializer(serializers.ModelSerializer):

    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipients = recipientsSerializers(
        write_only=True, required=False, many=True, queryset=UserModel.objects.all())
    trainergroups = trainergroupsSerializers(
        write_only=True, required=False, many=True, queryset=TrainGroup.objects.all())

    class Meta:
        model = Notification
        fields = ('level', 'recipients', 'trainergroups', 'sender',
                  'verb', 'description', 'target',
                  'action_object', 'public',
                  'data')
