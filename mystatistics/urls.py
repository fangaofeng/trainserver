from django.urls import path
from .api import GetStatistics
urlpatterns = [
    path('stats', GetStatistics.as_view()),

]
