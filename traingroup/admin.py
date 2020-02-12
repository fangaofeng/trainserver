from django.contrib import admin
from .models import TrainGroup
# Register your models here.


@admin.register(TrainGroup)
class TrainAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'group_no', 'department')


# @admin.register(TrainManagerPermission)
# class TrainPermissionAdmin(admin.ModelAdmin):

#     list_display = ('id',  'department', 'administrator')
