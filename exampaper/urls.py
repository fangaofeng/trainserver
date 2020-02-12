from rest_framework import routers
from django.urls import path
from .api import ExamPaPerViewSet, ZipfileUploadView
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'paper', ExamPaPerViewSet)

urlpatterns = [
    path('paper/upload', ZipfileUploadView.as_view(), name='paper_upload')
]
urlpatterns += router.urls
# urlpatterns += [path('paper/<str:paperid>/trainmanagers', ExamPaPerMemberModifyViewSet.as_view(
#     {'get': 'list', 'put': 'update', 'patch': 'partial_update'}), name='exampaper_trainmanagers')]
