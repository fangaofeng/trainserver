from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ExamPlanConfig(AppConfig):
    name = 'examplan'
    verbose_name = _('exam plans')
