from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from imagekit.admin import AdminThumbnail
from import_export import resources
from import_export.admin import ImportExportMixin, ImportExportModelAdmin
from mptt.admin import TreeRelatedFieldListFilter
from permissions.models import Role
from django.forms import CheckboxSelectMultiple, ModelMultipleChoiceField, ModelForm
from .models import Excelfile, User


class UserResource(resources.ModelResource):

    class Meta:
        model = User


class UserAdminForm(ModelForm):
    roles = ModelMultipleChoiceField(
        widget=CheckboxSelectMultiple, queryset=Role.objects.all())

    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    resource_class = UserResource
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'),
         {'fields': ('user_no', 'name', 'email', 'employee_position',  'info', 'avatar', 'department')}),
        (_('Permissions'),
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'roles')}),
        (_('Important dates'),
         {'fields': ('last_login', 'date_joined')}),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'roles', 'user_no', 'name')
        }),
    )

    list_display = ('id', 'username', 'user_no', 'name', 'email',
                    'employee_position', 'info',  'admin_thumbnail')
    list_filter = ('is_staff', 'is_superuser', 'is_active',
                   'groups', ('department', TreeRelatedFieldListFilter))
    search_fields = ('username', 'name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)
    form = UserAdminForm


@admin.register(Excelfile)
class ZipfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'excelfile')
