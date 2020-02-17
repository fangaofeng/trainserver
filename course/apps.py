from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CourseConfig(AppConfig):
    name = 'course'
    icon = 'iconfont icon-course'
    verbose_name = _("course manager")
