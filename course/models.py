from django.db import models
from utils import DigitserNoValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
# Create your models here.
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class Coursetype(models.Model):
    type = models.CharField(_('courseware type'), max_length=50, blank=True)
    typeid = models.PositiveSmallIntegerField(_('课程类别id，禁止修改'), blank=False, default=0)

    class Meta:
        verbose_name = _('course type ')
        verbose_name_plural = _('coursetype')

    def __str__(self):
        return str(self.type)


class Courseware(models.Model):
    coursewareNo_validator = DigitserNoValidator()

    # question = models.ForeignKey(Question, on_delete=models.CASCADE)

    courseware_no = models.CharField(
        _('courseware No.'),
        max_length=12,
        unique=True,
        help_text=_('Required. 课程编号（12位数字，不足在前面补0，如：201810000051）'),
        validators=[coursewareNo_validator],
        error_messages={
            'unique': _("A courseware  with that courseware_no No already exists."),
        },
    )
    name = models.CharField(_('courseware name'), max_length=50, blank=True)
    COURSEWARE_CATEGORY_CHOICES = (
        ('公开课', '公开课'),
        ('非公开课', '非公开课'),
    )
    category = models.CharField(
        max_length=10,
        choices=COURSEWARE_CATEGORY_CHOICES,
        default='公开课',
    )
    courseware_type = models.ForeignKey(Coursetype, on_delete=models.SET_NULL, blank=True,
                                        null=True,)
    intruduce = models.CharField(_('courseware intruduce'), max_length=1000, blank=True)
    applicable_user = models.CharField(_('courseware apply for object'), max_length=100, blank=True)

    class_hour = models.DecimalField(_('class need hour'), max_digits=4, decimal_places=2, null=True, blank=True)
    FILE_TYPE_CHOICES = (
        ('PDF', 'PDF'),
        ('MP4', 'MP4'),
    )
    file_type = models.CharField(
        max_length=3,
        choices=FILE_TYPE_CHOICES,
        default='MP4',
    )
    cover = models.FileField(upload_to='filecover/')
    courseware_file = models.FileField(upload_to='coursewarefile/')
    zipfile = models.FileField(upload_to='zipfile/', blank=True)
    teacherimg = models.FileField(upload_to='teacherimg/', blank=True)

    teachername = models.CharField(_('teacher name'), max_length=50, blank=True)
    teacherdesc = models.CharField(_('teacher intruduce'), max_length=1000, blank=True)
    STATUS_CHOICES = (
        ('拟制中', '拟制中'),
        ('已上架', '已上架'),
        ('已下架', '已下架'),
        ('已归档', '已归档')
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='拟制中',
    )
    User = get_user_model()

    trainmanagers = models.ManyToManyField(
        User,
        limit_choices_to={'role': 1},
        related_name='coursewares'
    )

    creater = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name='courseware_creater',
        blank=True,
        null=True,
    )
    property = JSONField(default={}, blank=True)
    config_ini = JSONField(default={}, blank=True)
    drag_flag = models.BooleanField(_(' drag flag'), default=True)
    create_time = models.DateTimeField(_('create'), default=timezone.now)
    # cover, teacherimg, courseware_file, config_dict

    class Meta:

        verbose_name = _('courseware ')
        verbose_name_plural = _('coursewares')

    def __str__(self):
        return self.name


class Zipfile(models.Model):

    zipfile = models.FileField(upload_to='./tempzipfile/', blank=True)

    def __str__(self):
        return str(self.id)
