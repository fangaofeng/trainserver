from rest_framework import permissions

from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
# from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework.authentication import TokenAuthentication
from django.contrib.admin import site
#import adminactions.actions as actions

# register all adminactions
# actions.add_to_site(site)

# from rest_framework_swagger.views import get_swagger_view
# schema_view = get_schema_view(title='Whlrest API')


# schema_viewswagger = get_swagger_view(title='whl Serverswagger  API')

urlpatterns = [

    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    #path('vali/', include('vali.urls')),
    # path('api/', include([
    #
    # ]))
    path("", include('users.urls')),
    path("train/", include(('traingroup.urls'))),
    # path("api/quest/", include('questions.urls')),
    path("orgs/", include('orgs.urls')),
    path("learn/", include('learn.urls')),
    path("", include('exampaper.urls')),
    path("exam/", include('examplan.urls')),
    path("course/", include('course.urls')),
    path("", include('notifications.urls')),

    path("blog/", include('blog.urls')),
    path("upload/", include('uploadfile.urls')),
    # path("user/", include('users.urls')),
    path("", include('mystatistics.urls')),
    path("geo/", include('geo.urls'))
    # Your stuff: custom urls includes go here
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.

    from rest_framework.schemas import get_schema_view
    from rest_framework.renderers import JSONOpenAPIRenderer
    from rest_framework.documentation import include_docs_urls
    schema_view = get_schema_view(
        title='whl Server  API',
        url='https://whl.org/api/',
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

        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [

        path('schema/', schema_view),
        path('apidocs/drf', include_docs_urls(title='whl Server  API')),
        path('apidocs/swaggeryasg', schema_viewyasg.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('apidocs/redocyasg', schema_viewyasg.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        re_path('swagger(?P<format>\.json|\.yaml)$', schema_viewyasg.without_ui(cache_timeout=0), name='schema-json'),
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))
                       ] + urlpatterns
