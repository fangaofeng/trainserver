from rest_framework.response import Response
from importlib import import_module
from django.conf import settings


def get_admin_site():

    site_module = getattr(settings, 'ADMIN_SITE',
                          'django.contrib.admin.site')
    mod, inst = site_module.rsplit('.', 1)
    mod = import_module(mod)
    return getattr(mod, inst)
