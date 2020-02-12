from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth import get_user_model
from course.models import Courseware
from exampaper.models import ExamPaPer
from rest_framework import status
from common.jsonrender import EmberJSONRenderer
from rest_framework.throttling import BaseThrottle, SimpleRateThrottle

from .models import Website_views
from django.utils import timezone
from permissions.permissions import RolePermission


class StatisticsThrottle(BaseThrottle):
    def allow_request(self, request, view):
        return True


class GetStatistics(APIView):
    """
    View to Statistics in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [RolePermission]
    renderer_classes = (EmberJSONRenderer,)

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        User = get_user_model()
        stuCount = User.objects.count()
        allUser = User.objects.count()
        trainerCount = User.objects.count()
        systermmanagerCount = User.objects.count()
        coursewareCount = Courseware.objects.count()
        courserwareonCount = Courseware.objects.filter(status='已上架').count()
        courserwarePdf = Courseware.objects.filter(file_type='PDF').count()
        courserwareMp4 = Courseware.objects.filter(file_type='MP4').count()
        exampaperCount = ExamPaPer.objects.count()
        exampaperonCount = ExamPaPer.objects.filter(status='已上架').count()
        websiteViews = Website_views.objects.count()
        statstime = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        data = dict(stuCount=stuCount, allUser=allUser, trainerCount=trainerCount,
                    systermmanagerCount=systermmanagerCount, coursewareCount=coursewareCount,
                    courserwareonCount=courserwareonCount, courserwareMp4=courserwareMp4, exampaperCount=exampaperCount,
                    exampaperonCount=exampaperonCount, websiteViews=websiteViews, statstime=statstime)

        return Response(data)
