''' Django notifications admin file '''
# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Notification, NotificationTask
from .signals import notifytask_done
from django.forms import CheckboxSelectMultiple, ModelForm, ModelMultipleChoiceField
from django.contrib.contenttypes.admin import GenericStackedInline
from django.contrib.contenttypes.models import ContentType
from django_reverse_admin import ReverseModelAdmin
from django.contrib.auth import get_user_model
User = get_user_model()


# class NotificationtaskInline(admin.StackedInline):
#     model = NotificationTask
#     fk_name = 'notifications'
#     # fields = ['reason', 'public', 'actor', 'verb', 'description', 'level']
#     readonly_fields = ['reason', 'public', 'actor', 'verb', 'description', 'level']
#     fieldsets = (
#         ('info', {
#             'fields': (('reason', 'public'), 'actor')
#         }),
#         ('content',  {
#             'fields': (('verb', 'level'), 'description', 'data')
#         }),
#     )


class NotificationAdmin(ReverseModelAdmin):
    inline_type = 'stacked'
    inline_reverse = [('task', {'fields': ['verb', 'description', 'public', 'reason', 'level'],
                                'readonly_fields': ['verb', 'description', 'public', 'reason', 'level']})]
    raw_id_fields = ('recipient',)
    list_display = ('recipient',
                    'unread', )
    list_filter = ('unread',  'created',)
    readonly_fields = ('recipient', 'created', 'modified', 'task')

    fieldsets = (
        ('info', {
            'fields': (('recipient', 'unread'), 'task')
        }),
        ('content',  {
            'fields': (('deleted', 'emailed'))
        }),

    )


# class NotificationAdmin(admin.ModelAdmin):
#     # inlines = [
#     #     NotificationtaskInline
#     # ]
#     raw_id_fields = ('recipient',)
#     list_display = ('recipient',
#                     'unread', )
#     list_filter = ('unread',  'created',)
#     readonly_fields = ('task', 'recipient', 'created', 'modified', 'task')

#     fieldsets = (
#         ('info', {
#             'fields': (('recipient', 'unread'), 'task')
#         }),
#         ('content',  {
#             'fields': (('deleted', 'emailed'))
#         }),

#     )


class NotificationtaskAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = NotificationTask
        fields = '__all__'


class actorform(GenericStackedInline):
    ct_field = "actor_content_type"
    ct_fk_field = "actor_object_id"
    model = NotificationTask


class NotificationtaskAdmin(admin.ModelAdmin):
    form = NotificationtaskAdminForm
    list_display = ('id', 'reason',
                    'level', 'verb', 'created')
    list_filter = ('level',)
    readonly_fields = ('created', 'modified', 'creater', 'actor', )
    exclude = ('target_content_type', 'target_id', 'actor_content_type', 'actor_object_id',
               'target', 'action_content_type', 'action_id', 'action',)
    # inlines = [
    #     actorform,
    # ]
    fieldsets = (
        (None, {
            'fields': (('reason', 'public'),)
        }),
        ('content',  {
            'fields': (('verb', 'level'), 'description', 'data')
        }),
        ('recipter', {
            'fields': ('departments', 'groups', 'users'),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        obj.creater = request.user
        obj.actor_content_type = ContentType.objects.get_for_model(request.user)
        obj.actor_object_id = request.user.pk,

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change=change)
        users = form.cleaned_data.get('users', None)
        if users:
            recipient_users = users.distinct()
        else:
            recipient_users = User.objects.none()
        departments = form.cleaned_data.get('departments', None)
        if departments:
            recipient_users_departments = User.objects.filter(department__id__in=departments.all()).distinct()
        else:
            recipient_users_departments = User.objects.none()
        groups = form.cleaned_data.get('groups', None)
        if groups:
            recipient_user_groups = User.objects.filter(istrainofgroups__id__in=groups.all()).distinct()
        else:
            recipient_user_groups = User.objects.none()

        recipient = (recipient_users | recipient_users_departments | recipient_user_groups).distinct()
        notifytask_done.send(sender=NotificationTask, instance=form.instance,
                             recipient=recipient,  change=change)


admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationTask, NotificationtaskAdmin)
