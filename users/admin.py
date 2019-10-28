from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Excelfile
from django.utils.translation import gettext_lazy as _
from imagekit.admin import AdminThumbnail
from import_export import resources
from import_export.admin import ImportExportModelAdmin,ImportExportMixin
from mptt.admin import TreeRelatedFieldListFilter
class UserResource(resources.ModelResource):

    class Meta:
        model = User
@admin.register(User)
class UserAdmin(BaseUserAdmin,ImportExportModelAdmin):
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    resource_class = UserResource
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('user_no', 'name', 'email','employee_position','role','info','avatar','department')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2','role','user_no', 'name' )
        }),
    )

    list_display = ('id','username', 'user_no', 'name', 'email','employee_position','info','avatar','role','admin_thumbnail')
    list_filter = ('role','is_staff', 'is_superuser', 'is_active', 'groups',('department', TreeRelatedFieldListFilter))
    search_fields = ('username', 'name','email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(Excelfile)
class ZipfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'excelfile')
