from django.urls import path
from rest_framework import routers
from .api import ExamPlanViewSet, ExamProgressViewSet,  ExamProgressViewGroupMemberSet, \
    ExamProgressViewQuestionSet, ExamProgressViewAggregationSet

# from cruds_adminlte.urls import crud_for_app
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'plan', ExamPlanViewSet)
router.register(r'progress', ExamProgressViewSet)


urlpatterns = router.urls
urlpatterns += [path('aggregation', ExamProgressViewAggregationSet.as_view(), name='examprogess_aggregation'),
                path('plan/<int:planid>/group/<int:groupid>/member',
                     ExamProgressViewGroupMemberSet.as_view({'get': 'list'}), name='examplan_group_progresses')]
