from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ExamPaperConfig(AppConfig):
    name = 'exampaper'
    icon = 'iconfont icon-exam2'
    verbose_name = _('exampaper manager')
