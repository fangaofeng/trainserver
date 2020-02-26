

from django.db.models import Q
import logging

from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from mptt.models import TreeManyToManyField, TreeForeignKey
from rest_framework.settings import api_settings
# from .classes import Permission
from .managers import RoleManager,  OperationManager

logger = logging.getLogger(__name__)


class Operation(models.Model):
    name = models.CharField(
        max_length=120, unique=True, verbose_name=_('name'))
    viewName = models.CharField(max_length=64, verbose_name=_('View name'))
    method = models.CharField(max_length=64, verbose_name=_('request method'))
    path = models.CharField(max_length=512, verbose_name=_('url patten'))
    action = models.CharField(max_length=64, verbose_name=_('Action'))

    objects = OperationManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('rest Operation')

        verbose_name_plural = _('rest Operation')

    def __str__(self):
        return self.name

    # def get_volatile_permission(self):
    #     return Permission.get(
    #         pk=self.name, proxy_only=True
    #     )

    def natural_key(self):
        return (self.viewName, self.action)

    def requester_has_this(self, user):
        # rest api default no superuser
        if hasattr(api_settings, 'user_settings') and api_settings.user_settings.get('superuser_rest', False):
            if user.is_superuser or user.is_staff:
                logger.debug(
                    'Permission "%s" granted to user "%s" as superuser or staff',
                    self, user
                )
                return True

        if user.is_authenticated:
            try:
                t = self.roles.filter(id=user.roles.id)
                if len(t) > 0:
                    return True
            except Exception as e:
                logger.debug(
                    'Fallthru: Permission "%s" not granted to user "%s"', self, user
                )
                return False
        return False

    def requester_filter_this(self, user):

        if self.requester_has_this(user):
            try:
                roles = user.roles
                queryset = roles.rolefilters.filter(Operation=self)
                # t = self.filterbackends.filter(role_id=user.user_options.roles.id)
                if len(queryset) > 0:
                    return queryset
            except Exception as e:
                logger.debug(
                    'Fallthru: Permission "%s" not granted to user "%s" "%s"', self, user, str(
                        e)
                )
                return False
        else:
            return None


class RoleFilterBackendModel(models.Model):

    name = models.CharField(max_length=120, verbose_name=_('filter name'))
    operation = models.ForeignKey(to=Operation,
                                  to_field='name',
                                  related_name='filterbackends',
                                  on_delete=models.CASCADE,
                                  verbose_name=_('operation'))

    class Meta:
        ordering = ('operation',)
        verbose_name = _('Role Filter BackendModel')
        verbose_name_plural = _('Role Filters BackendModel')
        unique_together = ('name', 'operation')

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(
        max_length=255, unique=True, verbose_name=_('name')
    )
    display = models.CharField(
        max_length=255,  verbose_name=_('display')
    )
    default = models.BooleanField(
        default=False,
        verbose_name=_('default role'))
    operations = models.ManyToManyField(to=Operation,
                                        through='RoleOperationshipWithFilter',
                                        through_fields=('role', 'operation'),
                                        related_name='roles',
                                        verbose_name=_('rest Permissions')
                                        )

    objects = RoleManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('permissions:roles')

    def natural_key(self):
        return (self.name)


def get_list():
    return {'operation': 'operation'}


class RoleOperationshipWithFilter(models.Model):
    role = models.ForeignKey(Role, to_field='name', on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, to_field='name', on_delete=models.CASCADE)
    filters = models.ManyToManyField(
        RoleFilterBackendModel,
        related_name="roles",
        blank=True,

    )
    description = models.CharField(max_length=512, blank=True, default='没有描述')

    class Meta:
        # auto_created = True
        unique_together = ['role', 'operation']
        verbose_name = _('Role and  Operation With Filter')
        verbose_name_plural = _('Role and  Operations With Filter')


class RestPermissionsMixin(models.Model):
    """
    Add the fields and methods necessary to support the Group and Permission
    models using the ModelBackend.
    """

    roles = models.ManyToManyField(
        Role,
        verbose_name=_('roles'),
        blank=True,
        help_text=_(
            'The roles this user belongs to. A user will get all permissions '
            'granted to each of their roles.'
        ),
        related_name="users",
        related_query_name="users",
    )

    class Meta:
        abstract = True

    def get_roles_operations(self):
        """
        Return a list of permission strings that this user has through their
        roles. Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        permissions = set()
        user_roles_field = get_user_model()._meta.get_field('roles')
        user_roles_query = 'roles__%s' % user_roles_field.related_query_name()
        return Operation.objects.filter(**{user_roles_query: user_obj})
        # for roles in self.roles:
        #     perms = roles.operations.values_list('viewName', 'action').order_by()
        #     permissions.update({"%s.%s" % (viewName, action) for viewName, action in perms})
        # return permissions

    def has_restPerm(self, perm):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """

        return self.is_active and perm in self.get_roles_operations()

    def has_restPerms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)
