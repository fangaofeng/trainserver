from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersAppConfig(AppConfig):

    name = "users"
    verbose_name = _("users")
