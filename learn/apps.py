from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LearnConfig(AppConfig):
    name = 'learn'
    verbose_name = _('learn manager')
