from rest_framework import routers
from .api import TrainGroupViewSet, TrainManagerViewSet, TrainGropMemberModifyViewSet
from django.urls import path
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'group', TrainGroupViewSet)
urlpatterns = router.urls
urlpatterns += [path('group/<str:groupid>/members', TrainGropMemberModifyViewSet.as_view(
    {'get': 'list', 'put': 'update', 'patch': 'partial_update'}), name='group_members')]
