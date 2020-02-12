from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel


class CreaterTimeStampedModel(TimeStampedModel):
    """ TimeStampedModel
    An abstract base class model that provides self-managed "created" and
    "modified" fields.
    """

    User = get_user_model()

    creater = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True
