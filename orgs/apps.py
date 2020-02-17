from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OrgsConfig(AppConfig):
    name = 'orgs'
    icon = 'iconfont icontongzhi1'
    verbose_name = _("organization manager")
