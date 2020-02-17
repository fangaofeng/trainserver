
from django.urls import path
from .api import GetUploadurl

urlpatterns = [
    path('uploadpath', GetUploadurl.as_view(), name='upload-path')]
