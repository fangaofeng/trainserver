from django.contrib import admin
from .models import Courseware, Coursetype,  Zipfile
# Register your models here.




@admin.register( Coursetype)
class CoursetypeAdmin(admin.ModelAdmin):
    pass
@admin.register( Courseware)
class CoursewareAdmin(admin.ModelAdmin):
    list_display = ('id', 'courseware_no','name','courseware_type')
@admin.register(Zipfile)
class ZipfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'zipfile')
