# -*- coding: utf-8 -*-
import xlrd
from .serializers import DepartmentSerializer, ExcelfileSerializer, DepartmentRecursiveSerializer, \
    DepartmentWriteSerializer
from .models import Department
from rest_framework import viewsets, generics
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from rest_framework.response import Response
import rest_framework_filters as filters
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from common.jsonrender import EmberJSONRenderer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from permissions.permissions import RolePermission
from permissions.filters import RoleFilterBackend
from django.shortcuts import get_object_or_404 as _get_object_or_404
from .filter import IsManagerFilterBackend, IsAdminFilterBackend, IsUserFilterBackend


trainmanager = openapi.Parameter('trainmanager',
                                 in_=openapi.IN_QUERY,
                                 description='是否返回管理员信息',
                                 type=openapi.TYPE_BOOLEAN)


@method_decorator(name='retrieve', decorator=swagger_auto_schema(manual_parameters=[trainmanager]))
class OrgViewSet(viewsets.ModelViewSet):

    renderer_classes = (EmberJSONRenderer,)
    queryset = Department.objects.all()
    serializer_class = DepartmentWriteSerializer
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerFilterBackend, IsUserFilterBackend, IsAdminFilterBackend]
    filter_backends = [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]

    filterset_fields = ('id', 'slug', 'name',)

    def get_serializer_class(self):
        if self.action == 'list':
            return DepartmentRecursiveSerializer
        if self.action == "retrieve":
            if self.request.query_params.get('trainmanager', None) == "true":
                return DepartmentSerializer
            return DepartmentRecursiveSerializer
        return super(OrgViewSet, self).get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve' and self.request.query_params.get('trainmanager', None) == "true":
            kwargs.update(expand='trainmanager')

        return super(OrgViewSet, self).get_serializer(*args, **kwargs)

    # def get_queryset(self):
    #     if self.action == 'list':
    #         queryset = self.filter_queryset(super().get_queryset())

    #         if not (self.request.query_params.get('id', None) or self.request.query_params.get('slug', None) or
    #                 self.request.query_params.get('name', None)):
    #             if hasattr(self.request.user, 'managerdepartment'):
    #                 queryset = queryset.filter(id=self.request.user.managerdepartment.id)
    #             else:
    #                 queryset = queryset.filter(id=self.request.user.department.id)
    #         return queryset
    #     return super().get_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        queryset = Department.objects.root_nodes()  # 查询所有上传成功的数据
        serializerorgs = DepartmentRecursiveSerializer(queryset, many=True)
        return Response(serializerorgs.data,  status=status.HTTP_200_OK, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        User = get_user_model()
        if (len(queryset) == 0):
            ui = 'onlyupload'
        else:
            usercount = User.objects.exclude(is_superuser=True).count()
            if usercount == 0:
                ui = 'canupload'
            else:
                ui = 'noupload'
        data = {'status': 'ok', 'ui': ui, 'data': serializer.data, 'NOCHANGE': True}

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        queryset = Department.objects.root_nodes()  # 查询所有上传成功的数据
        serializerorgs = DepartmentRecursiveSerializer(queryset, many=True)
        return Response(serializerorgs.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        queryset = Department.objects.root_nodes()  # 查询所有上传成功的数据
        serializerorgs = DepartmentRecursiveSerializer(queryset, many=True)
        return Response(serializerorgs.data, status=status.HTTP_200_OK)


class ExcelfileUploadView(generics.CreateAPIView):
    """The API view to handle font upload and convert the file into json format"""

    parser_classes = (MultiPartParser,)
    serializer_class = ExcelfileSerializer
    permission_classes = [RolePermission]

    def create(self, request, *args, **kwargs):
        count = self.importexcel()
        data = request.data
        data['importcount'] = count
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        queryset = Department.objects.root_nodes()  # 查询所有上传成功的数据
        serializerorgs = DepartmentRecursiveSerializer(queryset, many=True)  # 序列化所查询到的数据
        response_data = {'status': 'ok', 'importcount': count, 'importdata': serializerorgs.data}
        return Response(response_data, status=status.HTTP_200_OK, headers=headers)

    def importexcel(self):
        """
        读取文件内容
        :param kwargs:
        :return:
        """

        workbook = xlrd.open_workbook(filename=None, file_contents=self.request.FILES['excelfile'].read())
        '''从内存读取文件内容, file_contents会处理编码格式问题不可缺'''
        sheet = workbook.sheet_by_index(0)
        ncols = sheet.ncols
        nrows = sheet.nrows
        count = 0
        Department.objects.all().delete()
        for row in range(1, nrows):
            slug = ''
            parent = None
            parent1 = Department.objects.root_nodes()
            for col in range(0, ncols):
                name = sheet.cell_value(rowx=row, colx=col)
                if name == '' or name is None:
                    break
                if slug == '':
                    slug = name
                else:
                    slug = '/'.join([slug, name])

                try:
                    department = Department.objects.get(slug=slug)
                    parent = department
                except Department.DoesNotExist:
                    count += 1
                    parent = Department(name=name, parent=parent)
                    parent.clean()
                    parent.save()
        return count
