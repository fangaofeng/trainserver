import rest_framework_filters as filters
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from common.viewset import RetrieveListUpdateViewSet, CreateRetrieveListViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import ChoiceFilter, DjangoFilterBackend, FilterSet, ModelChoiceFilter
from permissions.permissions import RolePermission
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, NotificationTask
from .serializers import NotificationTaskSerializer, NotificationSerializer, NotificationTaskCreateSerializer
from .signals import notifytask_done
from django.contrib.auth import get_user_model
from .filter import IsOwnerFilterTaskBackend


class NotificationTaskViewSet(CreateRetrieveListViewSet):
    """
    delete: Remove a document from the selected cabinet.
    get: Returns the details of the selected cabinet document.
    """
    renderer_classes = (EmberJSONRenderer,)
    pagination_class = ListPagination
    queryset = NotificationTask.objects.all().order_by('-created')
    serializer_class = NotificationTaskSerializer
    roles_filterbackends = [IsOwnerFilterTaskBackend]
    permission_classes = [RolePermission]
    filter_backends = [filters.backends.RestFrameworkFilterBackend]
    filterset_fields = ['level']

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationTaskCreateSerializer
        if getattr(self, 'swagger_fake_view', False):  # 抑制swagger错误

            return NotificationTaskSerializer
        return super(NotificationTaskViewSet, self).get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            kwargs.update(fields=['id', 'level', 'reason', 'actor',
                                  'verb', 'description', 'target',
                                  'action', 'public',
                                  'data', 'created', 'status'])
        # if getattr(self, 'swagger_fake_view', False):  # 抑制swagger错误

        #     return NotificationTaskSerializer
        return super(NotificationTaskViewSet, self).get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        users = serializer.initial_data.get('users', None)
        User = get_user_model()
        if users:
            recipient_users = User.objects.filter(id__in=users).distinct()
        else:
            recipient_users = User.objects.none()

        departments = serializer.validated_data.get('departments', None)
        if departments:
            recipient_users_departments = User.objects.filter(department__in=departments).distinct()
        else:
            recipient_users_departments = User.objects.none()

        groups = serializer.validated_data.get('groups', None)
        if groups:
            recipient_user_groups = User.objects.filter(istrainofgroups__in=groups).distinct()
        else:
            recipient_user_groups = User.objects.none()

        recipient = (recipient_users | recipient_users_departments | recipient_user_groups).distinct()
        notifytask_done.send(sender=NotificationTask, instance=serializer.instance,
                             recipient=recipient)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class NotificationFilter(filters.FilterSet):

    unread = filters.BooleanFilter(field_name='unread')

    class Meta:
        model = Notification
        fields = ['unread']


class NotificationViewSet(RetrieveListUpdateViewSet):
    """
    delete: Remove a document from the selected cabinet.
    get: Returns the details of the selected cabinet document.
    """
    renderer_classes = (EmberJSONRenderer,)
    pagination_class = ListPagination
    queryset = Notification.objects.all().order_by('-created')
    serializer_class = NotificationSerializer
    # multiple_lookup_fields = ['level', 'unread']
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.backends.RestFrameworkFilterBackend]
    # filter_backends = [FilterSet]
    filterset_class = NotificationFilter
    # filterset_fields = ('unread',)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            self.queryset = Notification.objects.filter(recipient=self.request.user).order_by('-created')
        else:
            self.queryset = Notification.objects.none()
        return super(NotificationViewSet, self).get_queryset()

    @action(detail=False, methods=['PATCH'])
    def clear(self, request, *args, **kwargs):
        """
        所用设为已读

        """
        renderer_classes = (EmberJSONRenderer,)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.bulkchangestatus()
        Notification.objects.mark_all_as_unread(recipient=self.request.user)
        return Response(data={'count': 0}, status=status.HTTP_200_OK)
    # def get_serializer_class(self):
    #     if self.action == 'create':
    #         return NotificationCreateSerializer
    #     if getattr(self, 'swagger_fake_view', False):  # 抑制swagger错误

    #         return NotificationSerializer
    #     return super(NotificationViewSet, self).get_serializer_class()

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     # self.perform_create(serializer)
    #     recipients = serializer.validated_data.pop('recipients', [])
    #     trainergroups = serializer.validated_data.pop('trainergroups', [])

    #     for group in trainergroups:

    #         recipients.extend(list(group.trainers.all()))
    #     serializer.validated_data['recipient'] = recipients
    #     # notify.send(**serializer.validated_data)

    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
