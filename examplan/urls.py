from django.urls import path
from rest_framework import routers
from .api import ExamPlanViewSet, ExamProgressViewSet, ExamPlanViewGroupSet, ExamPlanViewGroupMemberProgressSet, ExamProgressViewQuestionSet, ExamProgressViewAggregationSet

#from cruds_adminlte.urls import crud_for_app
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'plan', ExamPlanViewSet)
#router.register(r'plan/progress', ExamProgressByPlanViewSet)
router.register(r'progress', ExamProgressViewSet)

urlpatterns = router.urls
urlpatterns += [path('plan/<int:planid>/groups', ExamPlanViewGroupSet.as_view(), name='examplan_traingroups'),
                path('plan/<int:planid>/group/<int:groupid>',
                     ExamPlanViewGroupMemberProgressSet.as_view(), name='examplan_group_progresses'),
                path('progress/<int:progressid>/questions',
                     ExamProgressViewQuestionSet.as_view(), name='examprogress_questions'),
                path('aggregation', ExamProgressViewAggregationSet.as_view(), name='examprogess_aggregation')
                ]
#urlpatterns += crud_for_app('examplan')
