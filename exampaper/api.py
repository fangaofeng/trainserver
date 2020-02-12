import base64
import os
import warnings
import zipfile as unzipfile

import pandas as pd
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from permissions.permissions import RolePermission
from rest_flex_fields import FlexFieldsModelViewSet
from rest_framework import generics, serializers, status, viewsets
from rest_framework.parsers import MultiPartParser
import rest_framework_filters as filters
from rest_framework.response import Response
from users.serializers import UserDetailsSerializer
from permissions.filters import RoleFilterBackend
from .filter import IsManagerFilterBackend
from .models import ExamPaPer, QuestionExam, Zipfile
from .serializers import (  # ExamPaPerMembersSerializer,
    ExamPaPerCreateSerializer,
    ExamPaPerSerializer,
    ZipfileSerializer,
    addquestionfunc
)


class ExamPaPerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    pagination_class = ListPagination
    renderer_classes = (EmberJSONRenderer,)
    queryset = ExamPaPer.objects.all()
    serializer_class = ExamPaPerSerializer
    permission_classes = [RolePermission]
    roles_filterbackends = [IsManagerFilterBackend]
    filter_backends = [RoleFilterBackend]

    def get_serializer_class(self):
        if self.action == 'create':
            return ExamPaPerCreateSerializer
        return super(ExamPaPerViewSet, self).get_serializer_class()

    def get_filter_backends(self):
        if self.action == 'list':
            return [RoleFilterBackend, filters.backends.RestFrameworkFilterBackend]
        return super().get_filter_backends()

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve':
            # if self.request.query_params.get('questiondict', False):
            #     kwargs.update(expand='questions', expandable_fields={
            #                   'questions': (serializers.SerializerMethodField,)})
            # else:
            kwargs.update(expand='questions')
        return super(ExamPaPerViewSet, self).get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
    # def retrieve(self, request, *args, **kwargs):
    #     super(ExamPaPerViewSet, self).retrieve(request, *args, **kwargs))


# exclude_param = openapi.Parameter('exclude',
#                                   in_=openapi.IN_QUERY,
#                                   description='不属于这个课程的管理员',
#                                   type=openapi.TYPE_BOOLEAN)


# @method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[exclude_param]))
# class ExamPaPerMemberModifyViewSet(viewsets.ModelViewSet):
#     """
#     获取群组成员支持分页
#     PUT:增加群组成员
#     PATCH：删除群组成员
#     """
#     renderer_classes = (EmberJSONRenderer,)
#     queryset = ExamPaPer.objects.all()
#     pagination_class = ListPagination
#     serializer_class = ExamPaPerMembersSerializer
#     permission_classes = [RolePermission]
#     # def get_queryset(self):
#     #     user = self.request.user
#     #     return TrainGroup.objects.filter(administrator=user)

#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return UserDetailsSerializer
#         else:
#             return ExamPaPerMembersSerializer

#     def get_object(self):
#         paperid = self.kwargs.get('paperid', None)
#         user = self.request.user

#         # if courseware.administrator.id != user.id:
#         #     raise Http404('you not allow to query this group.')
#         try:
#             paper = ExamPaPer.objects.get(id=paperid)
#             return paper
#         except ExamPaPer.DoesNotExist as e:
#             raise Http404('No paper {} matches the given query.'.format(paperid))

#     def get_queryset(self):
#         paperid = self.kwargs.get('paperid', None)
#         user = self.request.user

#         # if courseware.administrator.id != user.id:
#         #     raise Http404('you not allow to query this group.')

#         exclude = self.request.query_params.get('exclude', False)
#         try:
#             if exclude == 'true':
#                 User = get_user_model()
#                 # slug = user.managerdepartment.department.slug
#                 # return User.objects.filter(department__slug__startswith=slug).exclude(istrainofgroups__id=groupid)
#                 return User.objects.exclude(exampapers__id=paperid)
#             else:
#                 paper = ExamPaPer.objects.get(id=paperid)
#                 return paper.trainmanagers.all()
#         except ExamPaPer.DoesNotExist as e:
#             raise Http404('No trainmanagers matches the given query.')

#     def list(self, request, *args, **kwargs):
#         """
#         获取群组成员支持分页
#         """
#         queryset = self.filter_queryset(self.get_queryset())

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

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

    renderer_classes = (EmberJSONRenderer,)
    serializer_class = ZipfileSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = [RolePermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        cover, excel = self.unzipfile(request)
        data = self.read_excel(excel, cover)
        data.update(zipfileid=serializer.data['zipfileid'])
        return Response(data, status=status.HTTP_200_OK, headers=headers)

    def unzipfile(self, request):
        """
        解压文件返回文件路径
        :return:

        """
        unziparchive = None
        if request.data['zipfile']:
            unziparchive = unzipfile.ZipFile(request.data['zipfile'], 'r')
        if unziparchive is None:
            return dict()
        # 需要检查是否会有垃圾文件

        fhlhgks = None
        fhlhgsj = None
        file_list = unziparchive.namelist()
        if "fhlhgks.jpg" in file_list:
            cover = unziparchive.extract("fhlhgks.jpg")

        if "fhlhgsj.xlsx" in file_list:
            excel = unziparchive.extract("fhlhgsj.xlsx")

        unziparchive.close()
        return cover, excel

    def read_excel(self, excelfile, cover):
        paper_data = dict()
        real_score = 0
        try:
            questions = dict()
            paper_info = dict()
            ioexcel = pd.ExcelFile(excelfile)
            # 读取questions

            paper = ioexcel.parse(sheet_name='试题',
                                  dtype={'选项A': str, '选项B': str, '选项C': str, '选项D': str, '选项E': str, '选项F': str})
            paper['选项'] = paper.apply(lambda x: addquestionfunc(
                **{'A': x['选项A'], 'B': x['选项B'], 'C': x['选项C'], 'D': x['选项D'], 'E': x['选项E'], 'F': x['选项F']}), axis=1)

            paper_groupbytype = paper.groupby(paper['试题分类'])
            t = paper_groupbytype.get_group('多选题').reset_index(drop=True)
            t.index += 1
            multichoices = t.drop(['选项A', '选项B', '选项C', '选项D', '选项E', '选项F', '序号', '试题分类'], axis=1)
            multichoiceslist = []
            for key, value in multichoices.to_dict('index').items():
                value.update(order=key)

                multichoiceslist.append(value)
                real_score += value['分值']
            questions.update(multichoices=multichoiceslist)
            t = paper_groupbytype.get_group('单选题').reset_index(drop=True)
            t.index += 1
            singlechoices = t.drop(['选项A', '选项B', '选项C', '选项D', '选项E', '选项F', '序号', '试题分类'], axis=1)
            singlechoiceslist = []
            for key, value in singlechoices.to_dict('index').items():
                value.update(order=key)
                singlechoiceslist.append(value)
                real_score += value['分值']
            questions.update(singlechoices=singlechoiceslist)
            t = paper_groupbytype.get_group('判断题').reset_index(drop=True)
            t.index += 1
            judgements = t.drop(['选项A', '选项B', '选项C', '选项D', '选项E', '选项F', '序号', '试题分类'], axis=1)
            judgementslist = []
            for key, value in judgements.to_dict('index').items():
                value.update(order=key)
                judgementslist.append(value if value else '')
                real_score += value['分值']

            questions.update(judgements=judgementslist)

            # 读取试卷信息
            t = ioexcel.parse(sheet_name='介绍')
            td = t.set_index('标题')
            paper_info['试卷编号'] = td.loc['试卷编号']['内容']
            paper_info['试卷名称'] = td.loc['试卷名称']['内容']
            paper_info['试卷简介'] = td.loc['试卷简介']['内容']
            paper_info['适用对象'] = td.loc['适用对象']['内容']
            paper_info['试卷总分'] = td.loc['试卷总分']['内容']
            paper_info['合格分数'] = td.loc['合格分数']['内容']
            paper_info['考试时长'] = td.loc['考试时长']['内容']
            paper_info['适用课程编号'] = td.loc['适用课程编号']['内容']
            paper_info['适用课程名称'] = td.loc['适用课程名称']['内容']
            paper_info['试卷文件名称'] = td.loc['试卷文件名称']['内容']
            paper_info['实际总分'] = real_score
            with open(cover, "rb") as f:
                #     #paper_info['试卷封面'] = 'data:image/png;base64,%s' % base64.b64encode(f.read())
                paper_info['试卷封面'] = ','.join(['data:image/png;base64', str(base64.b64encode(f.read()), 'utf-8')])
            paper_data['paper_info'] = paper_info
            paper_data['questions'] = questions
            return paper_data
        except Exception as e:
            warnings.warn(str(e))

            return paper_data
        else:
            return paper_data
