from django.contrib import admin
from .models import Department, Excelfile
# Register your models here.
from django_mptt_admin.admin import DjangoMpttAdmin
from import_export.admin import ImportExportModelAdmin,ImportExportMixin
from import_export import resources

from mptt.admin import MPTTModelAdmin
class DepartmentResource(resources.ModelResource):

    class Meta:
        model = Department
        fields = ('id', 'name', 'parent',)

@admin.register(Department)
class OrgsAdmin(MPTTModelAdmin):
    mptt_level_indent = 40
    resource_class = DepartmentResource
    list_display = ('id', 'name', 'parent',)

@admin.register(Excelfile)
class ExcelfilefileAdmin(admin.ModelAdmin):
    list_display = ('id', 'excelfile')
