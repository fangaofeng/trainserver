from rest_framework import routers
from .api import OrgViewSet, OrganizationViewSet
from .api import ExcelfileUploadView
from django.urls import path
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'departments', OrgViewSet)
# router.register(r'departments/detail', DepartmentDetailView)
#
urlpatterns = router.urls
urlpatterns += [
    #     path('departments/', OrgViewSet.as_view({'get': 'list'})),
    path('excelupload', ExcelfileUploadView.as_view())
    #     #path('departments/<int:id>/', OrganizationViewSet.as_view({'get': 'list'})),
]
