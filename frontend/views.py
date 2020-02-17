from django.shortcuts import render
from django.views.decorators.http import condition
import pendulum


def etag_func(request, *args, **kwargs):
    return '1233333333333'


def last_modified_func(request, *args, **kwargs):
    return pendulum.datetime(2000, 1, 1)


# @condition(last_modified_func=last_modified_func)
def index(request):
    return render(request, 'frontend/index.html', {'title': '乐迪网络'})
