''' Django questions apps file '''
# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class questionsConfig(AppConfig):
    name = "questions"
    icon = 'iconfont icon-wenti'
    verbose_name = _("questions manager")

    def ready(self):
        super(questionsConfig, self).ready()
        # this is for backwards compability
        import questions.signals
        questions.ask = questions.signals.ask
