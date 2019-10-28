# -*- coding: utf-8 -*-
import xlrd
from .serializers import DepartmentSerializer, ExcelfileSerializer
from .models import Department
from rest_framework import viewsets, generics
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from common.jsonrender import EmberJSONRenderer


class OrgViewSet(viewsets.ModelViewSet):

    renderer_classes = (EmberJSONRenderer,)
    queryset = Department.objects.root_nodes()
    serializer_class = DepartmentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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

        return Response(data)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.root_nodes()
    serializer_class = DepartmentSerializer


class ExcelfileUploadView(generics.CreateAPIView):
    """The API view to handle font upload and convert the file into json format"""

    parser_classes = (MultiPartParser,)
    serializer_class = ExcelfileSerializer

    def create(self, request, *args, **kwargs):
        count = self.importexcel()
        data = request.data
        data['importcount'] = count
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        queryset = Department.objects.root_nodes()  # 查询所有上传成功的数据
        serializerorgs = DepartmentSerializer(queryset, many=True)  # 序列化所查询到的数据
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
                if name == '' or name == None:
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
