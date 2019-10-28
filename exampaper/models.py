from django.db import models

# Create your models here.
from django.utils import timezone
# Create your models here.
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django_extensions.db.models import TimeStampedModel
from common.models import CreaterTimeStampedModel
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator


class QuestionExam(CreaterTimeStampedModel):

    title = models.CharField(_('question name'), max_length=1000, blank=True)
    TYPE_CHOICES = (
        ('多选题', '多选题'),
        ('单选题', '单选题'),
        ('判断题', '判断题')
    )

    type = models.CharField(
        max_length=6,
        choices=TYPE_CHOICES,
        default='多选题',
    )
    # no = models.PositiveSmallIntegerField(_('No. in the paper'), validators=[MaxValueValidator(200)], blank=False)

    question_no = models.CharField(_('default No. of exampaper'), max_length=40, blank=False,
                                   null=False, unique=True)
    score = models.DecimalField(_('score'), max_digits=3, decimal_places=1,
                                default=1.0, null=False, blank=False)

    analysis = models.CharField(_('analysis for question'), max_length=300, blank=True,
                                null=True)

    options = JSONField(default=dict(), blank=True)
    answer = models.CharField(_('analysis for question'), max_length=300, blank=False)

    class Meta:
        verbose_name = _('question ')
        verbose_name_plural = _('questions')
        ordering = ['-created']

    def __str__(self):
        return self.title


class ExamPaPer(CreaterTimeStampedModel):

    name = models.CharField(_('exampaper name'), max_length=100, blank=True)
    exame_no = models.CharField(
        _('exam paper No.'),
        max_length=12,
        unique=True,
        help_text=_('Required. 考试计划编号'),
        error_messages={
            'unique': _("A user  with that user No already exists."),
        },
    )
    introduce = models.CharField(_('exampaper introduce'), max_length=1000, blank=True)
    STATUS_CHOICES = (
        ('拟制中', '拟制中'),
        ('已上架', '已上架'),
        ('已下架', '已下架'),
        ('已归档', '已归档')
    )
    status = models.CharField(
        max_length=9,
        choices=STATUS_CHOICES,
        default='拟制中',
    )
    cover = models.FileField(upload_to='filecover/')
    applicable_user = models.CharField(_('exam paper apply for object'), max_length=100, blank=True)
    total_score = models.PositiveSmallIntegerField(_('total score'), default=100, validators=[MaxValueValidator(200)])
    passing_score = models.PositiveSmallIntegerField(
        _('passing score'), default=60, validators=[MaxValueValidator(200)])
    duration = models.PositiveSmallIntegerField(_('durating time for exam'), default=60, validators=[
                                                MinValueValidator(1), MaxValueValidator(240)])
    examexcel_file = models.FileField(upload_to='examexcelfile/', blank=True)

    User = get_user_model()
    trainmanagers = models.ManyToManyField(
        User,
        limit_choices_to={'role': 1},
        related_name='exampapers',
        blank=True
    )
    # multichoices = models.ManyToManyField(
    #     QuestionExam,
    #     related_name='exampaper_multichoices',
    #     blank=True
    # )
    # singlechoices = models.ManyToManyField(
    #     QuestionExam,
    #     related_name='exampaper_singlechoices',
    #     blank=True
    # )
    # judgements = models.ManyToManyField(
    #     QuestionExam,
    #     related_name='exampaper_judgements',
    #     blank=True
    # )
    questions = models.ManyToManyField(
        QuestionExam,
        related_name='exampaper_questions',
        blank=True
    )

    def get_multichoices(self):
        q = self.questions.all().values('id').order_by('question_no')
        return q

    def get_singlechoices(self):
        q = self.questions.all().values('id').order_by('question_no')
        return q

    def get_judgements(self):
        q = self.questions.all().values('id').order_by('question_no')
        return q

    def get_quesitons(self):
        # q1 = self.multichoices.all().values('id')
        # q2 = self.singlechoices.all().values('id')
        # q3 = self.judgements.all().values('id')
        # q = (q1 | q2 | q3).order_by('question_no')
        q = self.questions.all().values('id').order_by('question_no')
        return q

    class Meta:
        verbose_name = _('exampaper ')
        verbose_name_plural = _('exampapers')

    def __str__(self):
        return self.name


class Zipfile(models.Model):

    zipfile = models.FileField(upload_to='./tempzipfile/', blank=True)

    def __str__(self):
        return str(self.id)
