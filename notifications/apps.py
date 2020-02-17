''' Django notifications apps file '''
# -*- coding: utf-8 -*-
from django.apps import AppConfig


class notificationsConfig(AppConfig):
    name = "notifications"
    icon = 'iconfont icontongzhi1'

    def ready(self):
        super(notificationsConfig, self).ready()
        # this is for backwards compability
        # import notifications.signals
        # notifications.notify = notifications.signals.notify
