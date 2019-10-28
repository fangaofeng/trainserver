from django.conf import settings


from django.core.exceptions import ImproperlyConfigured
from django.db import models

from django.utils import timezone

from django.contrib.postgres.fields import JSONField

from questions import settings as questions_settings

from questions.utils import id2slug
from django.contrib.auth import get_user_model

from django.contrib.contenttypes.fields import GenericForeignKey  # noqa


EXTRA_DATA = questions_settings.get_config()['USE_JSONFIELD']


def is_soft_delete():

    return questions_settings.get_config()['SOFT_DELETE']


def assert_soft_delete():
    if not is_soft_delete():
        msg = """To use 'deleted' field, please set 'SOFT_DELETE'=True in settings.
        Otherwise QuestionQuerySet.unread and QuestionQuerySet.read do NOT filter by 'deleted' field.
        """
        raise ImproperlyConfigured(msg)


class QuestionQuerySet(models.query.QuerySet):
    ''' Question QuerySet '''

    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self, include_deleted=False):
        """Return only unread items in the current queryset"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=True, deleted=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(unread=True)

    def read(self, include_deleted=False):
        """Return only read items in the current queryset"""
        if is_soft_delete() and not include_deleted:
            return self.filter(unread=False, deleted=False)

        # When SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
        # In this case, to improve query performance, don't filter by 'deleted' field
        return self.filter(unread=False)

    def mark_all_as_read(self, answerid=None):
        """Mark as read any unread messages in the current queryset.

        Optionally, filter these by answerid first.
        """
        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qset = self.unread(True)
        if answerid:
            qset = qset.filter(answerid=answerid)

        return qset.update(unread=False)

    def mark_all_as_unread(self, answerid=None):
        """Mark as unread any read messages in the current queryset.

        Optionally, filter these by answerid first.
        """
        qset = self.read(True)

        if answerid:
            qset = qset.filter(answerid=answerid)

        return qset.update(unread=True)

    def deleted(self):
        """Return only deleted items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=True)

    def active(self):
        """Return only active(un-deleted) items in the current queryset"""
        assert_soft_delete()
        return self.filter(deleted=False)

    def mark_all_as_deleted(self, answerid=None):
        """Mark current queryset as deleted.
        Optionally, filter by answerid first.
        """
        assert_soft_delete()
        qset = self.active()
        if answerid:
            qset = qset.filter(answerid=answerid)

        return qset.update(deleted=True)

    def mark_all_as_active(self, answerid=None):
        """Mark current queryset as active(un-deleted).
        Optionally, filter by answerid first.
        """
        assert_soft_delete()
        qset = self.deleted()
        if answerid:
            qset = qset.filter(answerid=answerid)

        return qset.update(deleted=False)

    def mark_as_unsent(self, answerid=None):
        qset = self.sent()
        if answerid:
            qset = qset.filter(answerid=answerid)
        return qset.update(emailed=False)

    def mark_as_sent(self, answerid=None):
        qset = self.unsent()
        if answerid:
            qset = qset.filter(answerid=answerid)
        return qset.update(emailed=True)


class Question(models.Model):
    """

    """
    # LEVELS = Choices('success', 'info', 'warning', 'error')
    # level = models.CharField(choices=LEVELS, default=LEVELS.info, max_length=20)
    User = get_user_model()
    answeruser = models.ForeignKey(
        User,
        blank=False,
        null=True,
        related_name='answer_questions',
        on_delete=models.SET_NULL
    )
    unanswer = models.BooleanField(default=True, blank=False, db_index=True)
    User = get_user_model()
    ask_user = models.ForeignKey(User,
                                 blank=False,
                                 null=True,
                                 related_name='ask_questions',
                                 on_delete=models.SET_NULL)
    learn_progress = models.ForeignKey('learn.LearnProgress',
                                 blank=False,
                                 null=True,
                                 related_name='questions',
                                 on_delete=models.SET_NULL)

    verb = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    ask_content = models.TextField(blank=True, null=True)
    ask_time = models.DateTimeField(default=timezone.now)

    answer_content = models.TextField(blank=True, null=True)

    answer_time = models.DateTimeField(default=timezone.now)
    position = JSONField(blank=True, null=True)
    # public = models.BooleanField(default=True, db_index=True)
    # deleted = models.BooleanField(default=False, db_index=True)
    # emailed = models.BooleanField(default=False, db_index=True)

    # data = JSONField(blank=True, null=True)

    class Meta:
        ordering = ('-ask_time',)
        app_label = 'questions'
        verbose_name = 'questions'
        verbose_name_plural = "questions"

    def __str__(self):
        return self.title

    @property
    def slug(self):
        return id2slug(self.id)

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()
