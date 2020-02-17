from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LearnConfig(AppConfig):
    name = 'learn'
    icon = 'iconfont icon-xuexi'
    verbose_name = _('learn manager')
