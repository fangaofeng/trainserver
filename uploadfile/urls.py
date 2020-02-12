from .api import UploadView
from rest_framework import routers
from django.urls import include, path


# router = routers.SimpleRouter(trailing_slash=False)
# router.register(r'file', UploadView, basename='upload')
urlpatterns = [
    path('file', UploadView.as_view()),
]
