from django.urls import path
from .api import GetCitys, GetProvince
urlpatterns = [
    path('province', GetProvince.as_view()),
    path('city/<str:province>', GetCitys.as_view()),
]
