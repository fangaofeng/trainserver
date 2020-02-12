from .api import CoursetypeViewSet, CoursewareViewSet, ZipfileUploadView
from rest_framework import routers
from django.urls import include, path
#from cruds_adminlte.urls import crud_for_app

router = routers.SimpleRouter(trailing_slash=False)
# router = routers.SimpleRouter(trailing_slash=False)

router.register(r'type', CoursetypeViewSet, basename='course_type')
router.register(r'ware', CoursewareViewSet, basename='course_ware')
# router.register(r'department', CoursewareMemberModifyViewSet, basename='course_department')
urlpatterns = [
    path('upload', ZipfileUploadView.as_view(), name='course_upload')
]
urlpatterns += router.urls
# urlpatterns += [path('<int:id>/departments', CoursewareMemberModifyViewSet.as_view(
#     {'get': 'list', 'put': 'update', 'patch': 'partial_update'}), name='courseware_departments')]
