from .base import *  # noqa
from .base import env
from django.urls import reverse_lazy
# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    'DJANGO_SECRET_KEY',
    default='MHGKv4iBHmuZwTFMAFHADLOzrG1k0XqJNEfJW5c8cDOUKWzdZlE2wXPWnpvn7vvQ')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    "*",
]
# Django Admin URL.
ADMIN_URL = 'admin/'
# CACHEOPS_
CACHEOPS_REDIS = "redis://localhost:6379/2"
CACHEOPS = {
    'orgs.Department': {'ops': 'all', 'timeout': 60*15},
    'permissions.Role': {'ops': 'all', 'timeout': 60*15},
    'permissions.Operation': {'ops': 'all', 'timeout': 60*15},
    'permissions.RoleFilterBackendModel': {'ops': 'all', 'timeout': 60*15},
    'permissions.RoleOperationshipWithFilter': {'ops': 'all', 'timeout': 60*15},
}
# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': ''
#     }
# }
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        "LOCATION": "redis://127.0.0.1:6379/1",  # env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {"max_connections": 100, "retry_on_timeout": True},
            # Mimicing memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

# -----------
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# django-cachalot
# CACHALOT_ENABLED = env.bool('CACHALOT_ENABLED', default=False)
# CACHALOT_TIMEOUT = env('CACHALOT_TIMEOUT', default=60 * 15)
# # CACHALOT_DATABASES = ['default']
# CACHALOT_ONLY_CACHABLE_TABLES = [
#     'admin_interface_theme', 'course_coursetype', 'permissions_operation', 'permissions_role',
#     'permissions_rolefilterbackendmodel', 'permissions_roleoperationshipwithfilter',
#     'permissions_roleoperationshipwithfilter_filters', 'orgs_department', 'traingroup_traingroup',
#     'traingroup_traingroup_trainers', 'authtoken_token']
# CACHE_MIDDLEWARE_SECONDS = 60 * 15

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa F405

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = env('EMAIL_HOST', default='mailhog')
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025
# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
# INSTALLED_APPS = ["whitenoise.runserver_nostatic.runserver_nostatic"] + INSTALLED_APPS  # noqa F405

# https://docs.djangoproject.com/en/dev/ref/csrf/
INSTALLED_APPS = ["corsheaders"] + INSTALLED_APPS  # noqa F405
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware']+MIDDLEWARE
tindex = MIDDLEWARE.index('django.middleware.csrf.CsrfViewMiddleware')
MIDDLEWARE.insert(tindex+1, 'corsheaders.middleware.CorsPostCsrfMiddleware')

# django allow all cors
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_REPLACE_HTTPS_REFERER = True
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    # 'VIEW',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)
# CORS_ORIGIN_WHITELIST = [

#     "http://localhost:8080",
#     "http://127.0.0.1:9000"
# ]
# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ['debug_toolbar']  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
#     'debug_toolbar.panels.profiling.ProfilingPanel'
#     # http://django-cachalot.readthedocs.org/en/latest/quickstart.html#usage
#     # 'cachalot.panels.CachalotPanel',
# ]
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',

    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ['127.0.0.1', 'localhost']
if env('USE_DOCKER') == 'yes':
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + '1' for ip in ips]

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ['django_extensions']  # noqa F405
# fgf
INSTALLED_APPS += ['drf_yasg']  # noqa F405 , 'rest_framework_swagger'
# Celery
# ------------------------------------------------------------------------------
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
CELERY_TASK_ALWAYS_EAGER = True
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
# Your stuff...
# ------------------------------------------------------------------------------
SWAGGER_SETTINGS = {
    'LOGIN_URL': reverse_lazy('admin:login'),
    'LOGOUT_URL': '/admin/logout',
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,

    'DEFAULT_INFO': 'testproj.urls.swagger_info',

    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
        'Query': {
            'type': 'apiKey',
            'name': 'auth',
            'in': 'query'
        }
    }
}

REDOC_SETTINGS = {
    'SPEC_URL': ('schema-json', {'format': '.json'}),
}
