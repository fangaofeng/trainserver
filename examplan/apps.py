from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ExamPlanConfig(AppConfig):
    name = 'examplan'
    icon = 'iconfont icon-plan1'
    verbose_name = _('exam plans')
