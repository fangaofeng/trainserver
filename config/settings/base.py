"""
Base settings to build other settings files upon.
"""

import environ

ROOT_DIR = environ.Path(
    __file__) - 3  # (whlrest/config/settings/base.py - 3 = whlrest/)
APPS_DIR = ROOT_DIR

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path('.env')))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL'),

}
DATABASES['default']['ATOMIC_REQUESTS'] = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'corsheaders',
    # 'fluent_dashboard',
    # 'admin_tools',
    # 'admin_tools.theming',
    # 'admin_tools.menu',
    # 'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 'debug_toolbar',
    # 'django.contrib.humanize', # Handy template tags
    # 'bdadmin',
    # 'grappelli',
    # 'simpleui',
    # 'nucleus',

    # 'bootstrap_admin',
    # 'bootstrap4',
    # 'nested_inline',

    'admin_interface',
    'colorfield',
    'admin_timeline',
    # 'adminlteui',
    # 'treebeard',
    # 'adminactions',
    # 'vali',
    # 'adminlte3',
    # # Optional: Django admin theme (must be before django.contrib.admin)
    # 'adminlte3_theme',
    'django.contrib.admin',

]
THIRD_PARTY_APPS = [

    # 'allauth',
    # 'allauth.account',
    # 'allauth.socialaccount',

    # 'django_mptt_admin',
    # 'crispy_forms',
    # 'django_select2',
    # pip install django-private-storage 媒体文件可以鉴权
    # pip install django-auditlog 日志
    # pip install django-cacheops 数据缓存
    # 'captcha',  验证码
    # 'easy_thumbnails',
    # 'image_cropping',  图片剪切
    'admin_honeypot',
    'django_json_widget',
    'mptt',
    'import_export',
    'rest_framework_filters',
    'rest_framework',              # 有自行修改部分，需要合并
    'rest_framework.authtoken',
    'imagekit',
    'simple_history',
    # 'dashing',
    # 'controlcenter',
    # 'django_json_widget',
    # 'dash',
    # 'dash.contrib.plugins.weather',
    # 'nested_admin',

]
LOCAL_APPS = [

    'exampaper.apps.ExamPaperConfig',
    'examplan.apps.ExamPlanConfig',
    'learn.apps.LearnConfig',
    'notifications.apps.notificationsConfig',
    'orgs.apps.OrgsConfig',
    'questions.apps.questionsConfig',
    'traingroup.apps.traingroupConfig',
    'course.apps.CourseConfig',
    'users.apps.UsersAppConfig',
    'blog.apps.BlogConfig',
    'uploadfile.apps.UploadfileConfig',
    'mystatistics.apps.MystatisticsConfig',
    'geo.apps.GeoConfig',
    'permissions.apps.PermissionsConfig',
    'frontend'
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {
    'sites': 'contrib.sites.migrations'
}


# CORS_ORIGIN_ALLOW_ALL
# 3
SIMPLEUI_HOME_TITLE = '网络培训'

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'users.User'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
# LOGIN_REDIRECT_URL = 'users:redirect'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
# LOGIN_URL = 'account_login'
REST_USE_JWT = False
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication'
    ),
    'UPLOADED_FILES_USE_URL': True,
    'DATE_FORMAT': '%Y-%m-%d',

    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',

    'TIME_FORMAT': '%H:%M:%S'


}
"""
DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M:%S',  # '2006-10-25 14:30:59'
    '%Y-%m-%dT%H:%M:%S',  # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',  # '2006-10-25 14:30'
    '%Y-%m-%d',  # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',  # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',  # '10/25/2006 14:30'
    '%m/%d/%Y',  # '10/25/2006'
    '%m/%d/%y %H:%M:%S',  # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',  # '10/25/06 14:30'
    '%m/%d/%y',  # '10/25/06'
    '%b %d %y',  # 'Oct 25 06'
    '%b %d %Y',  # 'Oct 25 2006'
    '%b %d %Y %I:%M%p',  # 'Oct 25 2006'
)
"""
# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# users_TOKEN_MODEL='users.UserToken'
# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mystatistics.VisitTimesMiddleware.VisitTimes',
    'simple_history.middleware.HistoryRequestMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'

]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                # 'admin_tools.template_loaders.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',

            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.core.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
# prefix url
FRONT_END_PREFIX = 'frond/'
REST_API_PREFIX = 'api/'
# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = 'admin/'

# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("""fgf""", 'fgf@whl.com'),
]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# Celery
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['taskapp.celery.CeleryAppConfig']
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ['json']
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERYD_TASK_SOFT_TIME_LIMIT = 60
# django-allauth
"""
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = 'username'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = 'whlrest.users.adapters.AccountAdapter'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_ADAPTER = 'whlrest.users.adapters.SocialAccountAdapter'

"""

# Your stuff...
# ------------------------------------------------------------------------------
VALI_CONFIG = {
    # the vali-admin themes  default, blue, purple, green,brown
    'theme': 'default',
    'dashboard': {'name': 'Dashboard', 'url': '/admin/'},
    # the order for applist  default, registry
    # display applist by group: True
    #  e.g. {group: True}
    # default check decorators  vali.decorator.vali_models_group on ModelAdmin
    #  * otherwize use group_marker in verbose_name_plural, (will be deprecated in future version 0.2.0)*
    #  * e.g.  {group: True, group_marker : '-'}
    #    verbose_name_plural = system-user
    #  * display the model "user" in group "system"
    'applist': {"order": "registry", "group": True},
    # default: //maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css
    # 'font_awesome_url': '/local/path/to/font-awesome-4.7.0/css/font-awesome.min.css',
}

# 流量控制
# REST_FRAMEWORK = {
#     'DEFAULT_THROTTLE_CLASSES': [
#         'rest_framework.throttling.AnonRateThrottle',
#         'rest_framework.throttling.UserRateThrottle',
#         # 'rest_framework.throttling.ScopedRateThrottle',
#     ],
#     'DEFAULT_THROTTLE_RATES': {
#         'anon': '100/day',
#         'user': '5000/day',
#         # 'login': '30/day',
#         # 'uploads': '30/day'
#     }
# }
DJANGO_NOTIFICATIONS_CONFIG = {'SOFT_DELETE': True}
# simpui
SIMPLEUI_ANALYSIS = False


# CONTROLCENTER_DASHBOARDS = (
#     ('mydash', 'dashboards.MyDashboard'),
# )
# ADMIN_TOOLS_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentIndexDashboard'
# ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentAppIndexDashboard'
# ADMIN_TOOLS_MENU = 'fluent_dashboard.menu.FluentMenu'


# upload path
UPLOAD_PATH = {
    'blog_cover': "blog",
    'courseware_cover': "courseware",
    'courseware_file': 'courseware',
    # 'teachimage': 'teachimg'
    'zipfilte': 'tempzipfile',
    'avatar': "avatar",
    'org_excelfile': 'org',
    'exam_excelfile': 'examexcel'}
