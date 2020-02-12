from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.urls import reverse


class GetUploadurl(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def geturl(self, request, name):
        return ''.join([request.scheme, '://', request.get_host(), reverse(name)])

    def get(self, request, format=None):
        """
        Return a list of all users.
        """

        UPLOAD_PATH = {
            'course': self.geturl(request, 'api:course_upload'),
            'paper': self.geturl(request, 'api:paper_upload'),
            'avatar': self.geturl(request, 'api:account_avatar'),
            'org': self.geturl(request, 'api:org_upload'),
            'user': self.geturl(request, 'api:user_upload')}
        return Response({'status': 'ok', 'data': UPLOAD_PATH})
