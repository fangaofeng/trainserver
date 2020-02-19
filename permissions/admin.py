from .models import Operation, Role, RoleFilterBackendModel, RoleOperationshipWithFilter
# from nested_admin import NestedStackedInline, NestedModelAdmin
from mptt.models import TreeManyToManyField
from django.utils.translation import gettext as _
from django.forms.models import (

    inlineformset_factory,
    modelform_defines_fields,
    modelform_factory,
    modelformset_factory
)
from collections import OrderedDict
from functools import partial, reduce, update_wrapper

from django import forms
from django.contrib import admin

from django.contrib.admin.utils import (
    NestedObjects,
    construct_change_message,
    flatten_fieldsets,
    get_deleted_objects,
    lookup_needs_distinct,
    model_format_dict,
    model_ngettext,
    quote,
    unquote
)
from django.core.exceptions import FieldDoesNotExist, FieldError, PermissionDenied, ValidationError
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple, ModelForm, ModelMultipleChoiceField, ModelChoiceField, CheckboxInput, \
    ChoiceField, BaseInlineFormSet, BaseModelFormSet, BooleanField, CharField, IntegerField
from django.forms.widgets import (
    HiddenInput, MultipleHiddenInput, SelectMultiple,
)
# from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from .inlineadmin import CheckboxInlineModelAdmin, CheckboxInlineAdminFormSet


# class TModelMultipleChoiceField(ModelMultipleChoiceField):

#     def __init__(self, queryset, **kwargs):
#         super(ModelMultipleChoiceField, self).__init__(queryset, empty_label='None', **kwargs)


class RoleOperationshipWithFilterAdminFormInline(ModelForm):
    filters = ModelMultipleChoiceField(required=False,
                                       widget=CheckboxSelectMultiple,
                                       queryset=RoleFilterBackendModel.objects.all()
                                       )
    # operation = CharField(disabled=True, strip=False, widget=forms.TextInput(attrs={'style': 'width:90%'}))
    #     widget=CheckboxSelectMultiple, queryset=Operation.objects.all())
    operation = CharField(disabled=True, strip=False, widget=forms.TextInput(attrs={'style': 'width:90%'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # if not hasattr(self.instance, 'operation'):
        #     print(self.instance)
        if self.instance and hasattr(self.instance, 'operation'):
            self.fields['filters'].queryset = RoleFilterBackendModel.objects.filter(operation=self.instance.operation)
            # self.fields['id'].initial = self.instance.id
            # self.fields['operation'].queryset = self.instance.operation
            # self.fields['operation'].disabled = True
            # print(self.instance.operation)
            self.fields['operation'].initial = self.instance.operation

    def clean(self):
        """
        give an operation instance
        """
        # operation = self.cleaned_data.get('operation', None)
        self.cleaned_data['operation'] = self.instance.operation
        return self.cleaned_data

    class Meta:
        model = RoleOperationshipWithFilter
        fields = ['operation', 'filters', 'description']
        # readonly_fields = ['operation']


# class RoleOperationshipWithFilterInline(admin.TabularInline):


class RoleOperationshipWithFilterInline(CheckboxInlineModelAdmin):

    model = RoleOperationshipWithFilter
    fk_name = 'role'
    show_change_link = True
    form = RoleOperationshipWithFilterAdminFormInline
    can_delete = True
    # readonly_fields = ['operation']
    empty_value_display = 'unknown'
    sortable_by = ('operation')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    # def groups_list(self, instance):
    #     return ','.join(instance.groups.values_list('name', flat=True))
    # form = RoleAdminForm
    inlines = [
        RoleOperationshipWithFilterInline,
    ]

    filter_horizontal = ('operations',)
    list_display = ('name', 'operations_list')
    filter_vertical = ('operations',)

    def operations_list(self, instance):
        return ','.join(instance.operations.values_list('name', flat=True))

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            has_add_permission = inline._has_add_permission(request, obj)
            has_change_permission = inline.has_change_permission(request, obj)
            has_delete_permission = inline.has_delete_permission(request, obj)
            has_view_permission = inline.has_view_permission(request, obj)
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = CheckboxInlineAdminFormSet(
                inline, formset, fieldsets, prepopulated, readonly, model_admin=self,
                has_add_permission=has_add_permission, has_change_permission=has_change_permission,
                has_delete_permission=has_delete_permission, has_view_permission=has_view_permission,
            )
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'viewName', 'action')
    list_display_links = list_display
    list_filter = ('action',)
    readonly_fields = ['id', 'viewName', 'action', 'name', 'method', 'path', 'action']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RoleFilterBackendModel)
class RoleFilterAdmin(admin.ModelAdmin):

    list_display = ('id', 'operation', 'name')
    list_display_links = list_display
    list_filter = ('name',)
    readonly_fields = ('id', 'name', 'operation',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class RoleOperationshipWithFilterAdminForm(ModelForm):
    filters = ModelMultipleChoiceField(required=False,
                                       widget=CheckboxSelectMultiple, queryset=RoleFilterBackendModel.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and hasattr(self.instance, 'operation'):
            self.fields['filters'].queryset = RoleFilterBackendModel.objects.filter(operation=self.instance.operation)

    class Meta:
        model = RoleOperationshipWithFilter
        fields = ['role', 'operation', 'filters', 'description']


@admin.register(RoleOperationshipWithFilter)
class RoleOperationshipWithFilterAdmin(admin.ModelAdmin):
    form = RoleOperationshipWithFilterAdminForm
    readonly_fields = ('role', 'operation')
    list_display = ('id', 'role', 'operation', 'has_filter')
    list_display_links = list_display
    list_filter = ('role',)
    sortable_by = ('operation', )

    def has_filter(self, obj):
        return len(obj.operation.filterbackends.all()) > 0
