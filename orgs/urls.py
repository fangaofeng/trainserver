from rest_framework import routers
from .api import OrgViewSet
from .api import ExcelfileUploadView
from django.urls import path
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'departments', OrgViewSet)
# router.register(r'departments/detail', DepartmentDetailView)
#
urlpatterns = router.urls
urlpatterns += [
    #     path('departments/', OrgViewSet.as_view({'get': 'list'})),
    path('upload', ExcelfileUploadView.as_view(), name='org_upload')
    #     #path('departments/<int:id>/', OrganizationViewSet.as_view({'get': 'list'})),
]
