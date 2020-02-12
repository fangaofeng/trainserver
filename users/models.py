import binascii
import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from model_utils import Choices
from mptt.models import TreeForeignKey
from rest_framework.authtoken.models import Token as DefaultTokenModel
from permissions.models import RestPermissionsMixin
from .utils import import_callable
from .validators import DigitserNoValidator

# Register your models here.


class User(AbstractUser, RestPermissionsMixin):
    """
    user_no 学员编号
    name 学员姓名
    username 登录账号
    password 登录密码
    department 所属部门
    employee_position 学员职务
    roles 学员类别
    info 个性化信息
    """
    userNo_validator = DigitserNoValidator()

    user_no = models.CharField(
        _('user No.'),
        max_length=12,
        unique=True,
        help_text=_('Required. 学员编号（12位数字，不足在前面补0，如：201810000051）'),
        validators=[userNo_validator],
        error_messages={
            'unique': _("A user  with that user No already exists."),
        },
    )
    name = models.CharField(_(' name'), max_length=50, blank=True, help_text="学员姓名")
    department = TreeForeignKey(
        'orgs.Department',
        on_delete=models.SET_NULL,
        related_name='members',
        blank=True,
        null=True,
    )

    employee_position = models.CharField(_('employee position'), max_length=50, blank=True)
    info = models.CharField(_('user info'), max_length=150, blank=True)
    # EMPLOYEE_ROLE_CHOICES = (
    #     (0, '系统管理员'),
    #     (1, '培训管理员'),
    #     (2, '学员')

    # )
    # EMPLOYEE_ROLE_CHOICES = Choices('系统管理员', '培训管理员', '学员')
    # roles = models.CharField(

    #     choices=EMPLOYEE_ROLE_CHOICES,
    #     default='学员',
    #     null=False,
    #     blank=False,
    #     max_length=20,
    #     help_text="学员类别"
    # )
    # roles = models.ForeignKey(on_delete=models.CASCADE, related_name='user', to_field='name',
    #                           to='permissions.Role', blank=True,  verbose_name=_('roles'), default='AnonymousUser')

    block_password_change = models.BooleanField(
        default=False,
        verbose_name=_('Forbid this user from changing their password.')
    )
    avatar = models.ImageField(
        upload_to="avatar", null=True, blank=True, default="avatar/user.jpg", verbose_name=_('Avatar')
    )
    thumbnail = ImageSpecField(source='avatar',
                               processors=[ResizeToFill(200, 200)],
                               format='JPEG',
                               options={'quality': 90})
    importid = models.CharField(_('import by excelid'), max_length=100, blank=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        ordering = ['username']

    def user_is_role(self, roles):
        return roles == self.roles

    def natural_key(self):
        return (self.user_no)


TokenModel = import_callable(
    getattr(settings, 'users_TOKEN_MODEL', DefaultTokenModel))


class UserToken(models.Model):
    """
    The default authorization token model.
    """
    token = models.CharField(_("token"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='user_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
        verbose_name = _("user Token")
        verbose_name_plural = _("user Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(UserToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.token


# 用户信息表
class Excelfile(models.Model):
    excelfile_dir = './users_excelfile/'
    excelfile = models.FileField(upload_to=excelfile_dir, blank=True)
    importid = models.CharField(_('id importing by excel '), max_length=100, blank=True)
    importcount = models.PositiveIntegerField(_('count of import user'), blank=False, default=0)

    class Meta:
        verbose_name = 'Excelfile'
        verbose_name_plural = "excelfile"

    class MPTTMeta:
        parent_attr = 'excelfile'

    def __str__(self):
        return self.id
