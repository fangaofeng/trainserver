from rest_framework import routers
from .api import LearnPlanViewSet, LearnProgressViewSet, LearnPlanViewGroupSet, LearnPlanViewGroupMemberProgressSet, LearnProgressViewAggregationSet
from django.urls import path
#from cruds_adminlte.urls import crud_for_app
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'plan', LearnPlanViewSet)
router.register(r'progress', LearnProgressViewSet)


urlpatterns = router.urls
urlpatterns += [path('plan/<int:learnplanid>/groups', LearnPlanViewGroupSet.as_view(), name='learnplan_traingroups'),
                path('plan/<int:learnplanid>/<int:groupid>',
                     LearnPlanViewGroupMemberProgressSet.as_view(), name='learnplan_group_progresses'),
                path('aggregation', LearnProgressViewAggregationSet.as_view(), name='learnprogess_aggregation')
                ]
#urlpatterns += crud_for_app('learn')
