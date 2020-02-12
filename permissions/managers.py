

import logging

from django.db import models
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


class RoleManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class StoredPermissionManager(models.Manager):
    def get_by_natural_key(self, namespace, name):
        return self.get(namespace=namespace, name=name)

    def get_for_holder(self, holder):
        ct = ContentType.objects.get_for_model(holder)
        return self.model.objects.filter(
            permissionholder__holder_type=ct
        ).filter(permissionholder__holder_id=holder.pk)


class OperationManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, viewname, action):
        return self.get(viewName=viewname, action=action)


class RestPermissionManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, viewname, action):
        return self.get(viewName=viewname, action=action)
    # def get_for_holder(self, holder):
    #     ct = ContentType.objects.get_for_model(holder)
    #     return self.model.objects.filter(
    #         permissionholder__holder_type=ct
    #     ).filter(permissionholder__holder_id=holder.pk)
