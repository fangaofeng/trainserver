from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
# Create your models here.
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from mptt.models import TreeForeignKey
from common.models import CreaterTimeStampedModel
from django.contrib.auth import get_user_model


class ExamPlan(TimeStampedModel):

    name = models.CharField(
        _('exampaper plan name.'),
        max_length=150,
        help_text=_('Required. 考试计划名称'),

        blank=False
    )
    exampaper = models.ForeignKey(
        'exampaper.ExamPaper',
        on_delete=models.CASCADE,
        related_name='exam_plans',
        blank=False
    )

    start_time = models.DateTimeField(_('start time '), blank=False)
    end_time = models.DateTimeField(_('end time '), blank=False)

    STATUS_CHOICES = (
        ('imitation', '拟制中'),
        ('assigned', '已指派'),
        ('learning', '考试中'),
        ('completed', '已完成'),
        ('archiving', '已归档')

    )

    status = models.CharField(_('考试计划状态'),
                              max_length=9,
                              default='assigned',
                              choices=STATUS_CHOICES,
                              help_text="考试状态"
                              )

    traingroups = models.ManyToManyField(
        'traingroup.TrainGroup',
        verbose_name=_('train group'),
        related_name='exam_plans',
        blank=False,
        help_text='计划实施的群组',
    )

    department = TreeForeignKey(
        'orgs.Department',
        models.SET_NULL,
        related_name='examplans',
        help_text='管理试卷的部门岗位',
        blank=True,
        null=True,
    )
    User = get_user_model()
    creater = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_plans',
        blank=False

    )

    class Meta:

        verbose_name = _('exam plan ')
        verbose_name_plural = _('exam plans')
        unique_together = ("creater", "name")
        ordering = ['-created']

    def __str__(self):
        return '_'.join([self.name, self.creater.username])


class ExamProgress(TimeStampedModel):

    plan = models.ForeignKey(
        ExamPlan,
        on_delete=models.CASCADE,
        related_name='progresses',
        blank=False,
        null=True
    )

    User = get_user_model()
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='examplan_progresses',
        blank=False,
        null=True
    )
    STATUS_CHOICES = (
        ('assigned', '已指派'),
        ('examing', '考试中'),
        ('completed', '已完成'),
        ('overdue', '超期未完成')


    )
    status = models.CharField(
        max_length=19,
        choices=STATUS_CHOICES,
        default='assigned',
        help_text="考试状态"
    )
    # traingroup = models.ForeignKey(
    #     'traingroup.TrainGroup',
    #     verbose_name=_('traingroup'),
    #     on_delete=models.CASCADE,
    #     help_text=_('Requered. belong to which of traingroup'),
    #     related_name='examplan_progresses',
    #     blank=False,
    # )
    start_time = models.DateTimeField(_('start time '), blank=True, null=True)
    end_time = models.DateTimeField(_('end time '), blank=True, null=True)
    score = models.PositiveIntegerField(_('score of test '), default=0)
    answers = JSONField(default=dict, blank=True)

    def change_status(self):
        if self.status == 'completed' and self.status == 'overdueCompleted':
            return

    def save(self, *args, **kwargs):
        # add default answers
        super(ExamProgress, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("plan", "trainer")
        verbose_name = _('exam plan progress')
        verbose_name_plural = _('exam_plan progresses')

    def __str__(self):
        return '{}_{}'.format(self.trainer_id, self.plan_id)
