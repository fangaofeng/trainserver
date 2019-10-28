from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.
from django.contrib.auth import get_user_model
from mptt.models import TreeForeignKey


class TrainManagerPermission(models.Model):
    """

    """
    created_time = models.DateTimeField(auto_now_add=True, null=True,
                                        verbose_name=_('Date created'))
    User = get_user_model()
    administrator = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='managerdepartment',
        limit_choices_to={'role': 1}
    )

    department = TreeForeignKey(
        'orgs.Department',
        models.CASCADE,
        verbose_name=_('administrator '),
        blank=False,

    )

    class Meta:
        verbose_name = _('train manager info ')
        verbose_name_plural = _('train_manager_info')

    def __str__(self):
        return '_'.join([self.administrator.username, self.department.name])


class TrainGroup(models.Model):
    """

    """
    name = models.CharField(_('name'), max_length=80)
    group_no = models.CharField(
        _('train group No.'),
        max_length=18,
        # unique=True,
        blank=True,
        help_text=_('Required. 培训群组'),
        error_messages={
            'unique': _("A user  with that user No already exists."),
        },
    )
    created_time = models.DateTimeField(auto_now_add=True, null=True,
                                        verbose_name=_('Date created'))
    User = get_user_model()
    administrator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('administrator of group'),
        limit_choices_to={'role': 1},
        related_name='managerofgroup',
        blank=False,
    )
    User = get_user_model()
    trainers = models.ManyToManyField(
        User,
        verbose_name=_('user id of trainer'),
        related_name='istrainofgroups',
        blank=False,
    )

    def get_trainers(self):
        return self.trainers.all()

    @classmethod
    def get_groupself(cls, ower):
        return cls.objects.filter(administrator=ower)

    class Meta:
        ordering = ['name']
        verbose_name = _('train_group')
        verbose_name_plural = _('train_groups')
        unique_together = ("administrator", "name")

    def __str__(self):
        return self.name
