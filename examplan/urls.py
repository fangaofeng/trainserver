from django.urls import path
from rest_framework import routers
from .api import ExamPlanViewSet, ExamProgressViewSet, ExamPlanViewGroupSet, ExamProgressViewGroupMemberSet, \
    ExamProgressViewQuestionSet, ExamProgressViewAggregationSet

# from cruds_adminlte.urls import crud_for_app
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'plan', ExamPlanViewSet)
# router.register(r'plan/progress', ExamProgressByPlanViewSet)
router.register(r'progress', ExamProgressViewSet)
router.register(r'plan/<int:planid>/groups',
                ExamPlanViewGroupSet, basename='examplan_traingroups')
router.register(r'plan/<int:planid>/group/<int:groupid>/member',
                ExamProgressViewGroupMemberSet, basename='examplan_group_progresses')
router.register(r'progress/<int:progressid>/questions',
                ExamProgressViewQuestionSet, basename='examprogress_questions')
urlpatterns = router.urls
urlpatterns += [path('aggregation', ExamProgressViewAggregationSet.as_view(), name='examprogess_aggregation')]
# [path('plan/<int:planid>/groups', ExamPlanViewGroupSet.as_view(), name='examplan_traingroups'),
# path('plan/<int:planid>/group/<int:groupid>',
#      LearnProgressViewGroupMemberSet.as_view({'get': 'list'}), name='examplan_group_progresses'),
# path('progress/<int:progressid>/questions',
#      ExamProgressViewQuestionSet.as_view(), name='examprogress_questions'),


# urlpatterns += crud_for_app('examplan')
