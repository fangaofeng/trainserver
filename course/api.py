from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
# from django_filters.rest_framework import (ChoiceFilter, DjangoFilterBackend,
#                                            FilterSet, ModelChoiceFilter)
from rest_framework import generics, status, viewsets
from rest_framework.parsers import FileUploadParser, MultiPartParser
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
from rest_framework.response import Response

import rest_framework_filters as filters

from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from common.viewset import ListUpdateViewSet
from permissions.permissions import RolePermission
from permissions.filters import RoleFilterBackend
from orgs.serializers import DepartmentSerializer
from .filter import IsManagerFilterBackend, IsUserFilterBackend
from .models import Coursetype, Courseware
from .serializers import (CoursetypeSerializer,
                          CoursewareModifySerializer,
                          CoursewareSerializer, CoursewareCreateSerializer,
                          ZipfileSerializer)


class CoursetypeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Coursetype.objects.all()
    serializer_class = CoursetypeSerializer
    permission_classes = [RolePermission]


class CourseFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ('noarchiving', '不包含已归档'),
    ]
    STATUS_CHOICES.extend(list(Courseware.STATUS_CHOICES))
    status = filters.ChoiceFilter(choices=STATUS_CHOICES, method='filter_status')
    recommend = filters.BooleanFilter(field_name='recommend')

    def filter_status(self, queryset, name, value):
        if value == 'noarchiving':
            return queryset.exclude(status='已归档')
        return queryset

    class Meta:
        model = Courseware
        fields = ['status', 'recommend']


class CoursewareViewSet(viewsets.ModelViewSet):
    """
    delete: Remove a document from the selected cabinet.
    get: Returns the details of the selected cabinet document.
    """
    roles_filterbackends = [IsManagerFilterBackend, IsUserFilterBackend]
    renderer_classes = (EmberJSONRenderer,)
    pagination_class = ListPagination
    queryset = Courseware.objects.all().order_by('-create_time')
    serializer_class = CoursewareCreateSerializer
    # parser_classes = (MultiPartParser,)
    multiple_lookup_fields = ['courseware_no']
    permission_classes = [RolePermission]
    filter_backends = [RoleFilterBackend]
    # filter_backends = [RoleFilterBackend]
    filterset_class = CourseFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CoursewareSerializer
        elif self.request.method == 'POST':
            return CoursewareCreateSerializer
        else:
            return CoursewareSerializer

    def get_filter_backends(self):
        if self.action == 'list':
            return [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
        return super().get_filter_backends()
    # post put区分serializer_class
    # def get_queryset(self):
    #     pass 对于培训管理员根据状态过滤

    # def get_object(self):
    #     """
    #      Returns the object the view is displaying.

    #      You may want to override this if you need to provide non-standard
    #      queryset lookups.  Eg if objects are referenced using multiple
    #      keyword arguments in the url conf.
    #      """
    #     queryset = self.filter_queryset(self.get_queryset())
    #     filter_kwargs = {}
    #     # Perform the lookup filtering.
    #     lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

    #     if lookup_url_kwarg in self.kwargs:
    #         filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

    #     for field in self.multiple_lookup_fields:
    #         field_data = self.request.data.get(field, None)
    #         if field_data:
    #             filter_kwargs[field] = field_data
    #     try:
    #         obj = self.queryset.get(**filter_kwargs)
    #         if obj:
    #             # May raise a permission denied
    #             self.check_object_permissions(self.request, obj)
    #     except self.queryset.model.DoesNotExist:
    #         obj = None

    #     return obj

    # def get_queryset(self):
    #     # user = self.request.user

    #     # if courseware.administrator.id != user.id:
    #     #     raise Http404('you not allow to query this group.')

    #     recommend = self.request.query_params.get('recommend', False)
    #     # try:
    #     if recommend == 'true':
    #         # User = get_user_model()
    #         # slug = user.managerdepartment.department.slug
    #         # return User.objects.filter(department__slug__startswith=slug).exclude(istrainofgroups__id=groupid)
    #         return Courseware.objects.filter(category='公开课')
    #     else:
    #         return Courseware.objects.all()
    #     # except Courseware.DoesNotExist as e:
    #     #     raise Http404('No trainmanagers matches the given query.')

    # def create(self, request, *args, **kwargs):

    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     serializer.is_valid(raise_exception=False)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_200_OK)


# class CourseMemberFilter(filters.FilterSet):

#     exclude = filters.BooleanFilter(field_name='departmen')

#     class Meta:
#         model = Courseware
#         fields = ['exclude']

# exclude_param = openapi.Parameter('exclude',
#                                   in_=openapi.IN_QUERY,
#                                   description='不属于这个课程的管理员',
#                                   type=openapi.TYPE_BOOLEAN)


# @method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[exclude_param]))
# class CoursewareMemberModifyViewSet(ListUpdateViewSet):
#     """
#     获取部门员支持分页
#     PUT:增加可查看部门
#     PATCH：删除删除可查看部门
#     """
#     renderer_classes = (EmberJSONRenderer,)
#     queryset = Courseware.objects.all()
#     pagination_class = ListPagination
#     serializer_class = CoursewareMembersSerializer
#     permission_classes = [RolePermission]
#     filter_backends = [RoleFilterBackend]
#     roles_filterbackends = [IsManagerFilterBackend]
#     lookup_url_kwarg = 'id'
#     # def get_queryset(self):
#     #     user = self.request.user
#     #     return TrainGroup.objects.filter(administrator=user)

#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return CoursewareMembersSerializer
#         else:
#             return CoursewareMembersSerializer

    # def get_object(self):
    #     courseid = self.kwargs.get('courseid', None)
    #     user = self.request.user
    #     courseware = Courseware.objects.get(id=courseid)
    #     # if courseware.administrator.id != user.id:
    #     #     raise Http404('you not allow to query this group.')
    #     return courseware

    # def get_queryset(self):
    #     courseid = self.kwargs.get('courseid', None)
    #     if courseid is None:
    #         raise Http404('No courseid matches the given query.')
    #     user = self.request.user

    #     # if courseware.administrator.id != user.id:
    #     #     raise Http404('you not allow to query this group.')

    #     exclude = self.request.query_params.get('exclude', False)
    #     try:
    #         if exclude == 'true':
    #             User = get_user_model()
    #             # slug = user.managerdepartment.department.slug
    #             # return User.objects.filter(department__slug__startswith=slug).exclude(istrainofgroups__id=groupid)
    #             return User.objects.exclude(coursewares__id=courseid)
    #         else:
    #             courseware = Courseware.objects.get(id=courseid)

    #             return courseware.departments.all()
    #     except Courseware.DoesNotExist as e:
    #         raise Http404('No departments matches the given query.')

    # def list(self, request, *args, **kwargs):
    #     """
    #     获取群组成员支持分页
    #     """
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    # def update(self, request, *args, **kwargs):
    #     """
    #     PUT:增加群组成员
    #     PATCH：删除群组成员

    #     """

    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}
    #     return Response({'status': 'ok'})


class ZipfileUploadView(generics.CreateAPIView):

    """The API view to handle font upload and convert the file into json format"""
    serializer_class = ZipfileSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = [RolePermission]
    renderer_classes = (EmberJSONRenderer,)
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
