from django.conf import settings
from rest_framework.authtoken.models import Token as DefaultTokenModel
from django.db import models
from .utils import import_callable
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from .validators import DigitserNoValidator
import binascii
import os
from mptt.models import TreeForeignKey
from model_utils import Choices
# Register your models here.


class User(AbstractUser):
    """
    user_no 员工编号
    name 员工姓名
    username 登录账号
    password 登录密码
    department 所属部门
    employee_position 员工职务
    role 员工类别
    info 个性化信息
    """
    userNo_validator = DigitserNoValidator()

    user_no = models.CharField(
        _('user No.'),
        max_length=12,
        unique=True,
        help_text=_('Required. 员工编号（12位数字，不足在前面补0，如：201810000051）'),
        validators=[userNo_validator],
        error_messages={
            'unique': _("A user  with that user No already exists."),
        },
    )
    name = models.CharField(_(' name'), max_length=50, blank=True, help_text="员工姓名")
    department = TreeForeignKey(
        'orgs.Department',
        models.SET_NULL,
        related_name='employee',
        blank=True,
        null=True,
    )

    employee_position = models.CharField(_('employee position'), max_length=50, blank=True)
    info = models.CharField(_('user info'), max_length=150, blank=True)
    # EMPLOYEE_ROLE_CHOICES = (
    #     (0, '系统管理员'),
    #     (1, '培训管理员'),
    #     (2, '员工')

    # )
    EMPLOYEE_ROLE_CHOICES = Choices('系统管理员', '培训管理员', '员工')
    role = models.CharField(

        choices=EMPLOYEE_ROLE_CHOICES,
        default='员工',
        null=False,
        blank=False,
        max_length=20,
        help_text="员工类别"
    )

    avatar = models.ImageField(
        upload_to="avatar", null=True, blank=True, verbose_name=_('Avatar')
    )
    thumbnail = ImageSpecField(source='avatar',
                               processors=[ResizeToFill(200, 200)],
                               format='JPEG',
                               options={'quality': 90})
    importid = models.CharField(_('import by excelid'), max_length=100, blank=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        ordering = ['username']

    def user_is_role(self, role):
        return role == self.role


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
