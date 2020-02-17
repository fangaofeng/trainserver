# -*- coding: utf-8 -*-

import re

import django
from admin_interface.cache import get_cached_active_theme, set_cached_active_theme
from admin_interface.models import Theme
from admin_interface.version import __version__
from django import VERSION, template
from django.conf import settings
from django.utils import translation
from importlib import import_module
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.apps import apps
register = template.Library()

simple_tag = register.simple_tag


@simple_tag(takes_context=True)
def get_admin_interface_languages(context):
    if not settings.USE_I18N:
        # i18n disabled
        return None
    if len(settings.LANGUAGES) < 2:
        # less than 2 languages
        return None
    try:
        set_language_url = reverse('set_language')
    except NoReverseMatch:
        # ImproperlyConfigured - must include i18n urls:
        # urlpatterns += [url(r'^i18n/', include('django.conf.urls.i18n')),]
        return None
    request = context.get('request', None)
    if not request:
        return None
    full_path = request.get_full_path()
    admin_nolang_url = re.sub(r'^\/([\w]{2})([\-\_]{1}[\w]{2})?\/', '/', full_path)
    if admin_nolang_url == full_path:
        # ImproperlyConfigured - must include admin urls using i18n_patterns:
        # from django.conf.urls.i18n import i18n_patterns
        # urlpatterns += i18n_patterns(url(r'^admin/', admin.site.urls))
        return None
    langs_data = []
    default_lang_code = settings.LANGUAGE_CODE
    current_lang_code = translation.get_language() or default_lang_code
    for language in settings.LANGUAGES:
        lang_code = language[0].lower()
        lang_name = language[1].title()
        lang_data = {
            'code': lang_code,
            'name': lang_name,
            'default': lang_code == default_lang_code,
            'active': lang_code == current_lang_code,
            'activation_url': '{}?next=/{}{}'.format(
                set_language_url, lang_code, admin_nolang_url)
        }
        langs_data.append(lang_data)
    return langs_data


@simple_tag(takes_context=True)
def get_admin_interface_theme(context):
    theme = get_cached_active_theme()
    if not theme:
        theme = Theme.get_active_theme()
        set_cached_active_theme(theme)
    return theme


@simple_tag(takes_context=False)
def get_admin_interface_version():
    return __version__


def get_admin_site():

    site_module = getattr(settings, 'BD_ADMIN_SITE',
                          'django.contrib.admin.site')
    mod, inst = site_module.rsplit('.', 1)
    mod = import_module(mod)
    return getattr(mod, inst)


site = get_admin_site()


@simple_tag(takes_context=False)
def get_app_list(request):

    app_list = site.get_app_list(request)
    # app_list=[]
    for i in range(len(app_list)):
        """
        app_name = app_dict['name']
        if len(app_name) > 23:
            app_name = app_label.title()
        """
        app_dict = app_list[i]
        app_label = app_dict['app_label']
        app_config = apps.get_app_config(app_label)
        app_icon = 'iconfont icondefault'
        if hasattr(app_config, 'icon'):
            app_icon = app_config.icon
        if app_label == 'authtoken':
            app_icon = 'iconfont iconauth'
        if app_label == 'auth':
            app_icon = 'iconfont iconauthenticationbg'
        if app_label == 'sites':
            app_icon = 'iconfont iconzhandianpeizhi'

        app_dict.update({
            'app_icon': mark_safe(app_icon),
            'active': False,
        })

        if request.path.startswith(app_dict['app_url']):
            app_dict['active'] = True

        for j in range(len(app_dict['models'])):
            model_dict = app_dict['models'][j]
            model_icon = 'fa fa-circle-o'
            if hasattr(model_dict, 'icon'):
                model_icon = model_dict.icon
                model_dict.update({
                    'icon': mark_safe(model_icon),
                    'active': False,
                })
            if request.path.startswith(model_dict['admin_url']):
                model_dict['active'] = True
            app_dict[j] = model_dict

        app_list[i] = app_dict

    # app_list.sort(key=lambda x: x['name'].lower())

    # # Sort the models alphabetically within each app.
    # for app in app_list:
    #     app['models'].sort(key=lambda x: x['name'])

    adminindex_url = reverse('admin:index', current_app=site.name)
    adminindex = {
        'name': 'home',
        'app_label': 'home',
        'app_icon': 'iconfont icon-Workbench2',
        'app_url': adminindex_url,
        'active': False,
    }
    if request.path == adminindex_url:
        adminindex['active'] = True
    app_list.insert(0, adminindex)
    return app_list


# @simple_tag(takes_context=False)
# def get_app2_list(request):
#     """Django 1.8 way to get application registered at default Admin Site."""
#     app_dict = {}

#     for model, model_admin in site._registry.items():
#         app_label = model._meta.app_label
#         has_module_perms = model_admin.has_module_permission(request)

#         if has_module_perms:
#             perms = model_admin.get_model_perms(request)

#             # Check whether user has any perm for this module.
#             # If so, add the module to the model_list.
#             if True in perms.values():
#                 info = (app_label, model._meta.model_name)
#                 model_icon = 'fa fa-circle-o'
#                 if hasattr(model_admin, 'icon'):
#                     model_icon = model_admin.icon
#                 model_dict = {
#                     'name': capfirst(model._meta.verbose_name_plural),
#                     'object_name': model._meta.object_name,
#                     'perms': perms,
#                     'icon': mark_safe(model_icon),
#                     'active': False,
#                 }
#                 if perms.get('change', False):
#                     try:
#                         model_dict['admin_url'] = reverse(
#                             'admin:%s_%s_changelist' % info, current_app=site.name)
#                         if request.path.startswith(model_dict['admin_url']):
#                             model_dict['active'] = True
#                     except NoReverseMatch:
#                         pass
#                 if app_label in app_dict:
#                     app_dict[app_label]['models'].append(model_dict)
#                 else:
#                     app_config = apps.get_app_config(app_label)

#                     app_name = app_config.verbose_name
#                     if len(app_name) > 23:
#                         app_name = app_label.title()
#                     app_name = app_name.replace('_', ' ')

#                     app_icon = 'fa fa-link'
#                     if hasattr(app_config, 'icon'):
#                         app_icon = app_config.icon

#                     app_dict[app_label] = {
#                         'name': app_name,
#                         'app_label': app_label,
#                         'app_icon': mark_safe(app_icon),
#                         'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=site.name),
#                         'has_module_perms': has_module_perms,
#                         'models': [model_dict],
#                         'active': False,
#                     }

#                     if request.path.startswith(app_dict[app_label]['app_url']):
#                         app_dict[app_label]['active'] = True

#     # Sort the apps alphabetically.
#     app_list = list(six.itervalues(app_dict))
#     app_list.sort(key=lambda x: x['name'].lower())

#     # Sort the models alphabetically within each app.
#     for app in app_list:
#         app['models'].sort(key=lambda x: x['name'])
#     adminindex_url = reverse('admin:Index',  current_app=site.name),
#     adminindex = {
#         'name': 'dashboard',
#         'app_label': 'dashboard',
#         'app_icon': 'fa fa-link',
#         'app_url': adminindex_url,
#         'active': False,
#     }
#     if request.path == adminindex_url:
#         adminindex['active'] = True
#     app_list.inset(0, adminindex)
#     return app_list
