from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields
# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import Coursetype, Courseware, Zipfile


@admin.register(Coursetype)
class CoursetypeAdmin(admin.ModelAdmin):
    pass
    # widgets = {
    #     'property': JSONEditorWidget()
    # }


# @admin.register(Courseware)
# class CoursewareAdmin(admin.ModelAdmin):
#     list_display = ('id', 'courseware_no', 'name', 'type')
#     formfield_overrides = {
#         fields.JSONField: {'widget': JSONEditorWidget},
#     }


@admin.register(Zipfile)
class ZipfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'zipfile')


@admin.register(Courseware)
class SimpleHistoryCoursewareAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'courseware_no', 'name', 'type')
    history_list_display = ["status"]

    # widgets = {
    #     'property': JSONEditorWidget(attrs={'width': 80}),
    # }
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
