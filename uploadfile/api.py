
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UploadfileSerializer


class UploadView(generics.CreateAPIView):

    """The API view to handle font upload and convert the file into json format"""
    serializer_class = UploadfileSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)
    throttle_scope = 'uploads'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
