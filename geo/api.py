
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status
from common.jsonrender import EmberJSONRenderer

import json


class GetCitys(APIView):
    """
    View to Statistics in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]
    renderer_classes = (EmberJSONRenderer,)

    def get(self, request, province, format=None):
        with open("geo/city.json", 'r', encoding="utf-8") as f:
            data = json.loads(f.read())

            return Response(data.get(province, {}))
        return Response({})


class GetProvince(APIView):
    """
    View to Statistics in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]
    renderer_classes = (EmberJSONRenderer,)

    def get(self, request,  format=None):
        with open("geo/province.json", 'r', encoding="utf-8") as f:
            data = json.loads(f.read())
            return Response(data)
        return Response({})
