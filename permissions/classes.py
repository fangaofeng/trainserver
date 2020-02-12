
# import itertools
# import logging

# from django.apps import apps
# from django.core.exceptions import PermissionDenied
# from django.utils.translation import ugettext_lazy as _

# from .exceptions import InvalidNamespace

# logger = logging.getLogger(__name__)


# class Permission(object):
#     _permissions = {}
#     _rest_permissions_cache = {}

#     @classmethod
#     def all(cls, as_choices=False):
#         if as_choices:
#             results = []

#             for namespace, permissions in itertools.groupby(cls.all(), lambda entry: entry.namespace):
#                 permission_options = [
#                     (permission.uuid, permission) for permission in permissions
#                 ]
#                 results.append(
#                     (namespace, permission_options)
#                 )

#             return results
#         else:
#             # Return sorted permisions by namespace.name
#             return sorted(
#                 cls._permissions.values(), key=lambda x: x.namespace.name
#             )

#     @classmethod
#     def check_permissions(cls, requester, permission):
#         user = requester.user
#         try:

#             if Operation.stored_permission.requester_has_this(requester):
#                 return True
#         except TypeError:
#             # Not a list of permissions, just one
#             if permissions.stored_permission.requester_has_this(requester):
#                 return True

#         logger.debug('User "%s" does not have permissions "%s"',
#                      requester,
#                      permissions)
#         raise PermissionDenied(_('Insufficient permissions.'))

#     @classmethod
#     def get(cls, pk, proxy_only=False):
#         if proxy_only:
#             return cls._permissions[pk]
#         else:
#             return cls._permissions[pk].stored_permission

#     @classmethod
#     def get_for_holder(cls, holder):
#         RestPermission = apps.get_model(
#             app_label='permissions', model_name='StoredPermission'
#         )
#         return RestPermission.get_for_holder(holder)

#     @classmethod
#     def invalidate_cache(cls):
#         cls._stored_permissions_cache = {}

#     @classmethod
#     def refresh(cls):
#         for permission in cls.all():
#             permission.stored_permission

#     def __init__(self, namespace, namee):
#         self.namespace = namespace
#         self.name = name
#         self.name = name
#         self.pk = self.uuid
#         self.__class__._permissions[self.uuid] = self

#     def __repr__(self):
#         return self.pk

#     def __str__(self):
#         return self.name

#     @property
#     def stored_permission(self):
#         RestPermission = apps.get_model(
#             app_label='permissions', model_name='RestPermission'
#         )

#         try:
#             return self.__class__._rest_permissions_cache[self.uuid]
#         except KeyError:
#             rest_permission, created = RestPermission.objects.get_or_create(
#                 namespace=self.namespace.name,
#                 name=self.name,
#             )
#             rest_permission.volatile_permission = self
#             self.__class__._rest_permissions_cache[
#                 self.uuid
#             ] = rest_permission
#             return rest_permission

#     @property
#     def uuid(self):
#         return '%s.%s' % (self.namespace.name, self.name)
