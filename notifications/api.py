from rest_framework import viewsets, generics
from .serializers import NotificationSerializer, NotificationCreateSerializer

from rest_framework.response import Response
from rest_framework import status
from common.jsonrender import EmberJSONRenderer
from django.shortcuts import get_object_or_404
from common.pagination import ListPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ModelChoiceFilter, ChoiceFilter
from common.viewset import CreateRetrieveListUpdateViewSet
import rest_framework_filters as filters
from .models import Notification
from .signals import notify
# class NotificationViewSet(viewsets.ModelViewSet):
#     serializer_class = NotificationSerializer

#     def get_queryset(self):
#         return self.request.user.notifications.unread()

#     @action(detail=True, methods=['post'])
#     def mark_as_read(self, request, pk=None):
#         notify = self.get_object()
#         notify.mark_as_read()
#         serializer = self.get_serializer(notify)
#         return Response(serializer.data)

#     def partial_update(self, request, pk=None):
#         print(pk)


class NotificationViewSet(CreateRetrieveListUpdateViewSet):
    """
    delete: Remove a document from the selected cabinet.
    get: Returns the details of the selected cabinet document.
    """
    renderer_classes = (EmberJSONRenderer,)
    pagination_class = ListPagination
    queryset = Notification.objects.all().order_by('-timestamp')
    serializer_class = NotificationSerializer
    multiple_lookup_fields = ['level']
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return self.request.user.notifications.active()

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        if getattr(self, 'swagger_fake_view', False):  # 抑制swagger错误

            return NotificationSerializer
        return super(NotificationViewSet, self).get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        recipients = serializer.validated_data.pop('recipients', [])
        trainergroups = serializer.validated_data.pop('trainergroups', [])

        for group in trainergroups:

            recipients.extend(list(group.trainers.all()))
        serializer.validated_data['recipient'] = recipients
        notify.send(**serializer.validated_data)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
