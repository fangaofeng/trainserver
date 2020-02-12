from django.urls import path
from rest_framework import routers
from .api import LearnPlanViewSet, LearnProgressViewSet, LearnPlanViewGroupSet, LearnProgressViewGroupMemberSet, \
    LearnProgressViewAggregationSet, PublicLearnProgressViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'plan', LearnPlanViewSet)
router.register(r'progress', LearnProgressViewSet)
router.register(r'publicprogress', PublicLearnProgressViewSet)

urlpatterns = router.urls
urlpatterns += [path('plan/<int:learnplanid>/groups', LearnPlanViewGroupSet.as_view(), name='learnplan_traingroups'),
                path('plan/<int:learnplanid>/group/<int:groupid>/member',
                     LearnProgressViewGroupMemberSet.as_view(), name='learnplan_group_progresses'),
                path('aggregation', LearnProgressViewAggregationSet.as_view(), name='learnprogess_aggregation')
                ]
