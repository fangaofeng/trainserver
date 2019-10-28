from django.db import models
from django.utils import timezone
# Create your models here.
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField


class LearnPlan(models.Model):

    # plan_no = models.CharField(
    #     _('learn plan No.'),
    #     max_length=12,
    #     unique=True,
    #     help_text=_('Required. 学习计划编号'),
    #     error_messages={
    #         'unique': _("A user  with that user No already exists."),
    #     },
    # )
    name = models.CharField(
        _('learn plan name.'),
        max_length=150,
        help_text=_('Required. 学习计划名称'),

        blank=False
    )
    course = models.ForeignKey(
        'course.Courseware',
        on_delete=models.CASCADE,
        related_name='learn_plans',
        blank=False

    )

    start_time = models.DateField(_('start time '), blank=False)
    end_time = models.DateField(_('end time '), blank=False)
    EXAME_CHOICES = (
        ('Yes', '需要'),
        ('No', '不需要'),

    )
    # orexame = models.IntegerField(
    #
    #     choices=EXAME_CHOICES,
    #     default=1,
    # )
    orexame = models.BooleanField(_('是否需要安排考试 '),
                                  default=False
                                  )
    STATUS_CHOICES = (
        ('imitation', '拟制中'),
        ('assigned', '已指派'),
        ('learning', '学习中'),
        ('completed', '已完成'),
        ('archiving', '已归档')

    )

    status = models.CharField(_('学习计划状态'),
                              max_length=9,
                              default='assigned',
                              choices=STATUS_CHOICES,
                              help_text="学习状态"
                              )

    # exampaper = models.OneToOneField(
    #     'exampaper.ExamPaper',
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    # )
    traingroups = models.ManyToManyField(
        'traingroup.TrainGroup',
        verbose_name=_('train group'),
        related_name='learn_plans',
        blank=False,
    )
    User = get_user_model()
    creater = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learn_plans',
        blank=False

    )
    create_time = models.DateTimeField(_('create'), default=timezone.now)

    class Meta:

        verbose_name = _('learn plan ')
        verbose_name_plural = _('learn_plan')
        unique_together = ("creater", "name")
        # order_by=('-create_time')

    def __str__(self):
        return '_'.join([self.name, self.creater.username])


class LearnProgress(models.Model):

    plan_no = models.ForeignKey(
        LearnPlan,
        on_delete=models.CASCADE,
        related_name='plan_progresses',
        blank=False,
        null=True
    )
    User = get_user_model()
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learnplan_progresses',
        blank=False,
        null=True
    )
    STATUS_CHOICES = (
        ('assigned', '已指派'),
        ('learning', '学习中'),
        ('completed', '已完成'),
        ('overdue', '已逾期'),


    )
    """
    待完成：已指派，学习中；
    已完成：已完成，超期已完成
    已逾期：超期未完成
    """
    status = models.CharField(
        max_length=19,
        choices=STATUS_CHOICES,
        default='assigned',
        help_text="学习状态"
    )
    traingroup = models.ForeignKey(
        'traingroup.TrainGroup',
        verbose_name=_('traingroup'),
        on_delete=models.CASCADE,
        help_text=_('Requered. belong to which of traingroup'),
        related_name='learnplan_progress',
        blank=False,
    )
    start_time = models.DateTimeField(_('start time '), blank=True, null=True)
    end_time = models.DateTimeField(_('end time '), blank=True, null=True)

    progress = JSONField("progress info", default=dict())
    create_time = models.DateTimeField(_('create'), default=timezone.now)
    type = models.CharField(max_length=20, default='course')

    def default_progress(self):
        if self.plan_no.course.file_type == 'PDF':
            self.progress = {'numpage': 1}
        if self.plan_no.course.file_type == 'MP4':
            self.progress = {'starttime': 0}
        return self.progress

    def change_status(self):
        if self.status == 'completed' and self.status == 'overdueCompleted':
            return

    def save(self, *args, **kwargs):
        if self.progress == {}:
            self.progress = self.default_progress()

        super(LearnProgress, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("plan_no", "trainer")
        verbose_name = _('learn plan progress')
        verbose_name_plural = _('learn_plan progresses')

    def __str__(self):
        return '{}_{}'.format(self.trainer_id, self.plan_no_id)
