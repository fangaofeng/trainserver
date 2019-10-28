from .api import CoursetypeViewSet, CoursewareViewSet, ZipfileUploadView, CoursewareMemberModifyViewSet
from rest_framework import routers
from django.urls import include, path
#from cruds_adminlte.urls import crud_for_app

router = routers.DefaultRouter(trailing_slash=False)
# router = routers.SimpleRouter(trailing_slash=False)

#router.register(r'type', CoursetypeViewSet)
router.register(r'ware', CoursewareViewSet, basename='course')

urlpatterns = [
    path('zipfileupload', ZipfileUploadView.as_view()),
]
urlpatterns += router.urls
urlpatterns += [path('ware/<str:courseid>/trainmanagers', CoursewareMemberModifyViewSet.as_view(
    {'get': 'list', 'put': 'update', 'patch': 'partial_update'}), name='courseware_trainmanagers')]

#urlpatterns += crud_for_app('course')
