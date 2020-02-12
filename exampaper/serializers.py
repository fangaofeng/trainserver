# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError

from rest_framework import serializers  # , exceptions
from .models import ExamPaPer, Zipfile, QuestionExam
import warnings
import pandas as pd
import zipfile as unzipfile
from django.core.files import File
import os
from rest_flex_fields import FlexFieldsModelSerializer
from common.serializers import OwnerFieldSerializer, OwnerFlexFSerializer
from django.contrib.auth import get_user_model
from rest_framework.utils import model_meta
from rest_framework.serializers import raise_errors_on_nested_writes, SerializerMethodField


def addquestionfunc(**kwarg):
    q = dict()
    for key, value in kwarg.items():
        if not value != value:
            q.update({key: value})
    return q


class QuestionExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionExam
        fields = '__all__'
        read_only_fields = ('question_no', 'created', 'creater')
        ordering = ['created']
        extra_kwargs = {'answer': {'write_only': True}}


class ExamPaPerCreateSerializer(OwnerFieldSerializer):
    zipfileid = serializers.IntegerField(write_only=True)

    class Meta:
        model = ExamPaPer
        fields = ['zipfileid', 'created', 'cover', 'creater', 'name', 'exame_no', 'introduce',
                  'status', 'applicable_user', 'total_score', 'passing_score', 'duration', 'departments']
        read_only_fields = ('created', 'cover', 'creater')
        ordering = ['created']

    def to_internal_value(self, data):

        ret = super(ExamPaPerCreateSerializer, self).to_internal_value(data)
        return ret

    def validate_courseware_no(self, value):
        return value

    def question_extrac(self, questions, exame_no):

        questionlist = []
        for value in questions:
            question = dict()
            # question.update(no=value['序号'])
            question.update(title=value['题目'])

            question.update(type=value['试题分类'])

            question.update(question_no='_'.join([exame_no, str(value['序号'])]))
            question.update(score=value['分值'])
            question.update(analysis=value['解析'])
            question.update(options=value['选项'])
            question.update(answer=value['答案'])

            questionlist.append(question)
        return questionlist

    def validate(self, attrs):
        zipfileid = attrs['zipfileid']
        exame_no = attrs['exame_no']

        cover, excel = self.unzipfile(zipfileid)
        multichoices, singlechoices, judgements, questions = self.read_questions(excel)
        attrs['cover'] = File(open(cover, mode='rb'))
        attrs['cover'].name = '_'.join([exame_no, os.path.basename(cover)])
        # attrs['multichoices'] = self.question_extrac(multichoices, exame_no)
        # attrs['singlechoices'] = self.question_extrac(singlechoices, exame_no)
        # attrs['judgements'] = self.question_extrac(judgements, exame_no)
        attrs['questions'] = self.question_extrac(questions, exame_no)
        del attrs['zipfileid']

        return attrs

    def save_questions(self, questions):
        querysetlist = []
        for question in questions:
            querysetlist.append(QuestionExam(**question))

        return QuestionExam.objects.bulk_create(querysetlist)

    def save(self, **kwargs):
        # create question
        # self.validated_data['multichoices'] = self.save_questions(self.validated_data['multichoices'])
        # self.validated_data['singlechoices'] = self.save_questions(self.validated_data['singlechoices'])
        # self.validated_data['judgements'] = self.save_questions(self.validated_data['judgements'])
        self.validated_data['questions'] = self.save_questions(validated_data['questions'])
        super(ExamPaPerCreateSerializer, self).save(**kwargs)

    def unzipfile(self, zipfileid):
        """
        解压文件返回文件路径
        :return:

        """
        zipfileobject = Zipfile.objects.get(id=zipfileid)  # 查询数据库找到ID=1的zipfile
        if zipfileobject is None:
            return None

        unziparchive = unzipfile.ZipFile(zipfileobject.zipfile.path, 'r')

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

        multichoices, singlechoices, judgements = self.read_questions(excel)
        return cover, excel

    def read_questions(self, excelfile):
        questions = dict()
        try:

            ioexcel = pd.ExcelFile(excelfile)
            # 读取questions
            paper = ioexcel.parse(sheet_name='试题',
                                  dtype={'选项A': str, '选项B': str, '选项C': str, '选项D': str, '选项E': str, '选项F': str})
            paper['选项'] = paper.apply(lambda x: addquestionfunc(
                **{'A': x['选项A'], 'B': x['选项B'], 'C': x['选项C'], 'D': x['选项D'], 'E': x['选项E'], 'F': x['选项F']}), axis=1)

            paper_groupbytype = paper.groupby(paper['试题分类'])
            t = paper_groupbytype.get_group('多选题').reset_index(drop=True)
            multichoices = t.drop(['选项A', '选项B', '选项C', '选项D', '选项E', '选项F'], axis=1)
            t = paper_groupbytype.get_group('单选题').reset_index(drop=True)
            t.index += 1
            singlechoices = t.drop(['选项A', '选项B', '选项C', '选项D', '选项E', '选项F'], axis=1)
            questions.update(singlechoices=singlechoices)
            t = paper_groupbytype.get_group('判断题').reset_index(drop=True)
            t.index += 1
            judgements = t.drop(['选项A', '选项B', '选项C', '选项D', '选项E', '选项F'], axis=1)

            questions.update(judgements=judgements)

            # 试卷信息来自界面，无需再获取

            return multichoices.to_dict(orient='records'), singlechoices.to_dict(orient='records'), judgements.to_dict(
                orient='records'), questions
        except Exception as e:
            warnings.warn(str(e))

            return None, None, None


class ExamPaPerSerializer(OwnerFlexFSerializer):
    # questionsdict = serializers.SerializerMethodField()

    class Meta:
        model = ExamPaPer
        fields = ['id', 'created', 'cover', 'creater', 'name', 'exame_no', 'introduce', 'departments',
                  'status', 'applicable_user', 'total_score', 'passing_score', 'duration']
        read_only_fields = ('created', 'cover', 'creater')
        ordering = ['created']

        expandable_fields = {
            # 'departments': (QuestionExamSerializer, {'source': 'departments', 'many': True}),
            'questionsdict': (SerializerMethodField,),
            # 'singlechoices': (QuestionExamSerializer, {'source': 'questions', 'many': True}),
            # 'judgements': (QuestionExamSerializer, {'source': 'questions',  'many': True}),
            'questions': (QuestionExamSerializer, {'source': 'questions', 'many': True})
        }

    def get_questions(self, instance):
        questionsdict = {}

        q = instance.questions.all()
        for item in q:
            templist = questionsdict.get(item.type, [])
            qserialize = QuestionExamSerializer(item)
            templist.append(qserialize.data)
            questionsdict.update({item.type: templist})

        return questionsdict


# class ExamPaPerMembersSerializer(serializers.ModelSerializer):

#     User = get_user_model()
#     departments = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=User.objects.all())

#     class Meta:
#         model = ExamPaPer
#         fields = ['departments']
#         ordering = ['created_time']
#         depth = 1

#     def update(self, instance, validated_data):
#         raise_errors_on_nested_writes('update', self, validated_data)
#         info = model_meta.get_field_info(instance)
#         for attr, value in validated_data.items():
#             if attr in info.relations and info.relations[attr].to_many:
#                 field = getattr(instance, attr)
#                 if self.partial:
#                     field.remove(*value)  # 对象不存在时，没有提示
#                 else:
#                     field.add(*value)
#             else:
#                 setattr(instance, attr, value)
#         if not self.partial:
#             instance.save()

#         return instance


class ZipfileSerializer(serializers.ModelSerializer):
    zipfileid = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Zipfile
        fields = ['zipfile', 'zipfileid']
        read_only_fields = ['zipfileid']
        extra_kwargs = {
            'zipfile': {'write_only': True}
        }
