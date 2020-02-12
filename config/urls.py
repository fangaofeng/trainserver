from rest_framework import permissions

from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
# from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework.authentication import TokenAuthentication
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from dashing.utils import router
from controlcenter.views import controlcenter
urlpatterns_api = [
    path("", include('users.urls')),
    path("train/", include('traingroup.urls')),

    path("orgs/", include('orgs.urls')),
    path("learn/", include('learn.urls')),
    path("", include('exampaper.urls')),
    path("exam/", include('examplan.urls')),
    path("course/", include('course.urls')),
    path("", include('notifications.urls')),

    path("blog/", include('blog.urls')),
    # path("upload/", include(('uploadfile.urls','upload'), namespace='api')),
    path("", include('mystatistics.urls')),
    # path("geo/", include(('geo.urls','geo'), namespace='api')),

    path("config/", include('admin_interface.urls'))
]
# urlpatterns_api=[
# path("api/", include(('users.urls', 'user'), namespace='api')),
# path("api/train/", include(('traingroup.urls', 'traingroup'), namespace='api')),

# path("api/orgs/", include(('orgs.urls', 'org'), namespace='api')),
# path("api/learn/", include(('learn.urls', 'learn'), namespace='api')),
# path("api/", include(('exampaper.urls', 'paper'), namespace='api')),
# path("api/exam/", include(('examplan.urls', 'examplan'), namespace='api')),
# path("api/course/", include(('course.urls', 'course'), namespace='api')),
# path("api/", include(('notifications.urls', 'notify'), namespace='api')),

# path("api/blog/", include(('blog.urls', 'blog'), namespace='api')),
# # path("api/upload/", include(('uploadfile.urls','upload'), namespace='api')),
# path("api/", include(('mystatistics.urls', 'statistics'), namespace='api')),
# # path("api/geo/", include(('geo.urls','geo'), namespace='api')),

# path("api/config/", include(('admin_interface.urls', 'config'), namespace='api'))
# ]
urlpatterns = [
    # path('admin_tools/', include('admin_tools.urls')),
    # path('dashboard/', include(router.urls)),
    # path(settings.ADMIN_URL, include('admin_honeypot.urls', namespace='admin_honeypot')),
    # path('secret/', admin.site.urls),
    path(settings.ADMIN_URL+'timeline', include('admin_timeline.urls')),
    path(settings.ADMIN_URL, admin.site.urls),
    path(settings.FRONT_END_PREFIX, include(('frontend.urls', 'frontend'), namespace='front')),
    path(settings.REST_API_PREFIX, include((urlpatterns_api, 'api'), namespace='api'))
    # api start

    # api end
    # Your stuff: custom urls includes go here
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.

    from rest_framework.schemas import get_schema_view
    from rest_framework.renderers import JSONOpenAPIRenderer, BrowsableAPIRenderer, CoreAPIJSONOpenAPIRenderer
    from rest_framework.documentation import include_docs_urls
    schema_view = get_schema_view(
        title='whl Server  API',
        url='https://whl.org/api/',
        public=True,
        renderer_classes=[JSONOpenAPIRenderer])

    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view as get_schema_viewyasg
    schema_viewyasg = get_schema_viewyasg(
        openapi.Info(
            title="whl API",
            default_version='v1',
            description="Test description",
            terms_of_service="https://www.whl.com/policies/terms/",
            contact=openapi.Contact(email="contact@whl.com"),
            license=openapi.License(name="BSD License"),
        ),
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                    path('schema/', schema_view),
                    #             path(
                    # 'apidocs/drf',
                    # include_docs_urls(
                    #     public=True,
                    #     title='whl Server  API', authentication_classes=[],
                    #     permission_classes=[])),
                    path(
                    'apidocs/swaggeryasg', schema_viewyasg.with_ui('swagger', cache_timeout=0),
                    name='schema-swagger-ui'),
                    path(
                    'apidocs/redocyasg', schema_viewyasg.with_ui('redoc', cache_timeout=0),
                    name='schema-redoc'),
                    re_path(
                    'swagger(?P<format>\.json|\.yaml)$', schema_viewyasg.without_ui(cache_timeout=0),
                    name='schema-json'),
                    path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")},),
                    path(
                    "403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")},),
                    path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")},),
                    path("500/", default_views.server_error),
                    path('admin/dashboard/', controlcenter.urls),
                    # path('grappelli/', include('grappelli.urls')),  # grappelli URLS
                    # path('dashboard/', include('dash.urls')),
                    # django-dash RSS contrib plugin URLs:
                    # path('dash/contrib/plugins/rss-feed/',
                    #      include('dash.contrib.plugins.rss_feed.urls')),

                    # django-dash public dashboards contrib app:
                    # path('', include('dash.contrib.apps.public_dashboard.urls')),
                    path('nested_admin/', include('nested_admin.urls')),
                    ]

    if "debug_toolbar" in settings.INSTALLED_APPS:
        # import debug_toolbar

        # urlpatterns += [path("__debug__/", include(debug_toolbar.urls))
        #                 ]
        pass
