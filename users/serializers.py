from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from imagekit.models import ProcessedImageField
from .models import TokenModel
from .utils import import_callable
from .models import Excelfile
from common.selffield import ChoiceField
# Get the UserModel
UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Authentication without using allauth

        if username:
            user = self._validate_username(username, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'users.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(
                        _('E-mail is not verified.'))

        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """
    # role_display = serializers.CharField()
    # roles = serializers.ListField(required=True)
    roles = serializers.StringRelatedField(many=True)
    token = serializers.StringRelatedField(source='key', read_only=True)

    class Meta:
        model = TokenModel
        fields = ('token', 'roles',)


class AccountInfoDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    department_name = serializers.ReadOnlyField(source='department.slug')
    # role_display = serializers.ReadOnlyField(source='roles.name')
    thumbnail = serializers.ImageField(read_only=True)
    unreadnoticescount = serializers.SerializerMethodField()

    def get_unreadnoticescount(self, obj):
        return obj.notifications.unread().count()

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'name', 'avatar', 'user_no', 'employee_position',
                  'email', 'roles', 'info', 'thumbnail', 'department_name', 'unreadnoticescount', )
        read_only_fields = ('username', 'roles',  'employee_position',
                            'user_no', 'department_name', 'thumbnail',)


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    department_name = serializers.ReadOnlyField(source='department.slug')
    # role_display = serializers.ReadOnlyField(source='roles.name')
    # unreadnoticescount = serializers.SerializerMethodField()

    # def get_unreadnoticescount(self, obj):
    #     return obj.notifications.unread().count()
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'name', 'avatar', 'user_no', 'employee_position', 'email',
                  'roles', 'info', 'thumbnail', 'department', 'department_name',)
        read_only_fields = ('id',   'department_name', 'thumbnail',)


class UserListSerializer(serializers.Serializer):

    users = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=UserModel.objects.all())

    class Meta:
        fields = ['users']

    def deleteusers(self):
        for user in self.validated_data['users']:
            user.delete()


class UserAvtarSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = UserModel
        fields = (
            'id', 'avatar')


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """
        Required to allow using custom USER_DETAILS_SERIALIZER in
        JWTSerializer. Defining it here to avoid circular imports
        """
        users_serializers = getattr(settings, 'users_SERIALIZERS', {})
        JWTUserDetailsSerializer = import_callable(
            users_serializers.get('USER_DETAILS_SERIALIZER',
                                  UserDetailsSerializer))
        user_data = JWTUserDetailsSerializer(
            obj['user'], context=self.context).data
        return user_data


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(
            data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            uid = force_text(uid_decoder(attrs['uid']))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'uid': ['Invalid value']})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        return self.set_password_form.save()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, 'OLD_PASSWORD_FIELD_ENABLED', False)
        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', False)
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (self.old_password_field_enabled,
                                       self.user,
                                       not self.user.check_password(value))

        if all(invalid_password_conditions):
            raise serializers.ValidationError('Invalid password')
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs)

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)


class ExcelfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Excelfile
        fields = ('excelfile', 'importid', 'importcount')
        read_only_fields = ['importid', 'importcount']
        write_only_fields = ['excelfile']
        ref_name = 'user_excelfile'
