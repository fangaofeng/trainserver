# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError

import configparser
import os
import zipfile as unzipfile
from config.settings import base
import json
import configparser

from django.core.files import File

from django.conf import settings
# from django.core.files.temp import TemporaryFile
from rest_framework import serializers  # , exceptions
from users.serializers import UserDetailsSerializer
from .models import Coursetype, Courseware, Zipfile
from django.contrib.auth import get_user_model
import moviepy.editor as mp
from PyPDF2 import PdfFileReader
from common.selffield import ChoiceField
from django.contrib.auth import get_user_model
from common.serializers import ADDDELSerializer
from orgs.models import Department


class CoursewareCreateSerializer(serializers.ModelSerializer):
    serializer_choice_field = ChoiceField
    zipfileid = serializers.IntegerField(write_only=True)
    User = get_user_model()
    # trainmanagers = serializers.PrimaryKeyRelatedField(
    #     write_only=True, required=False, many=True, queryset=User.objects.all())
    # departments = serializers.PrimaryKeyRelatedField(
    #     required=False, many=True, queryset=Department.objects.all())
    category = ChoiceField(choices=Courseware.COURSEWARE_CATEGORY_CHOICES)
    file_type = ChoiceField(choices=Courseware.FILE_TYPE_CHOICES)
    status = ChoiceField(choices=Courseware.STATUS_CHOICES)
    # courseware_type = serializers.CharField(source='courseware_type.type')
    creater = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Courseware
        fields = ['id', 'zipfileid',   "departments", "courseware_no", "name",  "category",
                  "intruduce",
                  "applicable_user",
                  "class_hour",
                  "file_type",
                  "teachername",
                  "teacherdesc",
                  'teacherimg',
                  "cover",
                  "status",
                  "drag_flag",
                  'courseware_file',
                  "type", "property", "create_time", 'creater', 'recommend']
        read_only_fields = ['id', 'create_time', "cover",
                            'cover', 'teacherimg',  'courseware_file', "property", 'creater']

        ordering = ['create_time'],
        extra_kwargs = {
            # 'trainmanagers': {'write_only': True},
            # 'departments': {'write_only': True},
            'zipfileid': {'write_only': True}}

    def to_internal_value(self, data):
        # type = data.get('courseware_type', None)
        # courstype = Coursetype.objects.get(type=type)
        # data['courseware_type'] = courstype.type
        return super(CoursewareCreateSerializer, self).to_internal_value(data)

    # def validate_courseware_no(self, value):
    #     return value

    def validate(self, attrs):
        zipfileid = attrs['zipfileid']
        courseware_no = attrs['courseware_no']

        cover, teacherimg, courseware_file, config_dict, zipfile, file_type = self.unzipfile(zipfileid)
        if file_type != attrs['file_type']:
            raise serializers.ValidationError(
                '上传文件与配置文件不一致'
            )
        try:
            if file_type == 'MP4':
                movie = mp.VideoFileClip(courseware_file)

                attrs['property'] = {'duration': movie.duration}
                movie.close()
            if file_type == 'PDF':
                with open(courseware_file, "rb") as f:
                    pdf = PdfFileReader(f)
                    numpages = pdf.getNumPages()
                attrs['property'] = {'numpages': numpages}
        except Exception as e:
            raise serializers.ValidationError(
                '解析上传文件错误'
            )
        attrs['cover'] = File(open(cover, mode='rb'))
        attrs['cover'].name = '_'.join([courseware_no, os.path.basename(cover)])
        attrs['teacherimg'] = File(open(teacherimg, mode='rb'))
        attrs['teacherimg'].name = '_'.join([courseware_no, os.path.basename(teacherimg)])
        attrs['zipfile'] = File(open(zipfile, mode='rb'))
        attrs['zipfile'].name = '_'.join([courseware_no, os.path.basename(zipfile)])
        attrs['courseware_file'] = File(open(courseware_file, mode='rb'))
        attrs['courseware_file'].name = '_'.join([courseware_no, os.path.basename(courseware_file)])
        attrs['config_ini'] = config_dict
        del attrs['zipfileid']

        return attrs

    def unzipfile(self, zipfileid):
        """
        解压文件返回文件路径
        :return:

        """
        zipfileobject = Zipfile.objects.get(id=zipfileid)  # 查询数据库找到ID=1的zipfile
        if zipfileobject is None:
            return None

        unziparchive = unzipfile.ZipFile(zipfileobject.zipfile.path, 'r')  # 拼接路径得到所需解压文件绝对路径
        # tempdir = os.path.join(['./',zipfileobject.zipfile.name[:-4]])
        # a=os.path.basename(zipfileobject.zipfile.path)
        curdir = os.path.dirname(zipfileobject.zipfile.path)
        mkdirname = os.path.splitext(zipfileobject.zipfile.path)[0]
        unzipdir = os.path.join(curdir, mkdirname)
        # 补充检查文件名是否规范
        file_list = unziparchive.namelist()
        if "fhlhg.jpg" in file_list:
            cover = unziparchive.extract("fhlhg.jpg", unzipdir)

        if "fb.jpg" in file_list:
            teacherimg = unziparchive.extract("fb.jpg", unzipdir)
        if "fhlhg.mp4" in file_list:
            courseware_file = unziparchive.extract("fhlhg.mp4", unzipdir)
            file_type = 'MP4'
        if "fhlhg.pdf" in file_list:
            courseware_file = unziparchive.extract("fhlhg.pdf", unzipdir)
            file_type = 'PDF'
        if "config.ini" in file_list:
            config_ini = unziparchive.extract("config.ini", unzipdir)
            # config_dir = os.path._getfullpathname(config_ini)

            conf = configparser.ConfigParser()
            conf.read(config_ini, encoding='utf-8')  # 读取ini文件

            config_dict = dict(conf._sections)  # 转换为字典 格式 需要提取数据转换
            # print(dic_con)
            # config_json = json.dumps(config_dic)

        unziparchive.close()
        return cover, teacherimg,  courseware_file, config_dict, zipfileobject.zipfile.path, file_type

    # def create(self, validated_data):
    #
    #     trainmanagers = validated_data.pop('trainmanagers',[])
    #     # 更改为事务,需要处理重复数据和异常
    #     instance = super(CoursewareCreateSerializer, self).create(validated_data)
    #     querysetlist=[]
    #
    #     for trainmanager in trainmanagers:
    #         querysetlist.append(CoursePermission(courseware=instance,trainmanager=trainmanager))
    #     CoursePermission.objects.bulk_create(querysetlist)
    #     return instance
    #
    # def save(self, **kwargs):
    #     return super(CoursewareCreateSerializer, self).save(**kwargs)
    #
    # def update(self, instance, validated_data):
    #
    #     trainmanagers = validated_data.pop('trainmanagers',[])
    #     # 更改为事务,需要处理重复数据和异常
    #     instance = super(CoursewareCreateSerializer, self).update(instance,validated_data)
    #     querysetlist=[]
    #     instance.trainmanagers.clean()
    #     for trainmanager in trainmanagers:
    #         querysetlist.append(CoursePermission(courseware=instance, trainmanager=trainmanager))
    #     CoursePermission.objects.bulk_create(querysetlist)
    #     return instance


class CoursewareModifySerializer(serializers.ModelSerializer):
    serializer_choice_field = ChoiceField
    category = ChoiceField(choices=Courseware.COURSEWARE_CATEGORY_CHOICES)
    file_type = ChoiceField(choices=Courseware.FILE_TYPE_CHOICES)
    status = ChoiceField(choices=Courseware.STATUS_CHOICES)

    class Meta:
        model = Courseware
        fields = ["id", "name",  "category", "departments",
                  "intruduce",
                  "applicable_user",
                  "class_hour",
                  "file_type",
                  "teachername",
                  "teacherdesc",
                  'teacherimg',
                  "cover",
                  "status",
                  "drag_flag", 'create_time', 'courseware_file', "property", "recommend"
                  ]
        read_only_fields = ('id',
                            'cover', 'create_time', 'teacherimg',  'courseware_file', "property")

        ordering = ['create_time'],


class CoursewareSerializer(serializers.ModelSerializer):
    serializer_choice_field = ChoiceField
    category = ChoiceField(choices=Courseware.COURSEWARE_CATEGORY_CHOICES)
    file_type = ChoiceField(choices=Courseware.FILE_TYPE_CHOICES)
    status = ChoiceField(choices=Courseware.STATUS_CHOICES)
    type = serializers.CharField(source='type.type')
    creater = serializers.CharField(source='creater.name')

    class Meta:
        model = Courseware
        fields = ['id', "courseware_no", "departments", "name",  "category",
                  "intruduce",
                  "applicable_user",
                  "class_hour",
                  "file_type",
                  "teachername",
                  "teacherdesc",
                  'teacherimg',
                  "cover",
                  "status",
                  "drag_flag", 'courseware_file', 'creater',
                  "type", "property", "recommend"]
        read_only_fields = ('id', "courseware_no", "name",  "category",
                            "intruduce",
                            "applicable_user",
                            "class_hour",
                            "file_type",
                            "teachername",
                            "teacherdesc",
                            'teacherimg',
                            "cover",
                            "status",
                            "drag_flag", 'courseware_file', 'creater',
                            "type", "property")

        ordering = ['create_time'],


class CoursetypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coursetype
        fields = ['type']


# class CoursewareMembersSerializer(ADDDELSerializer):

#     User = get_user_model()
#     # trainmanagers = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=User.objects.all())
#     departments = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=Department.objects.all())

#     class Meta:
#         model = Courseware
#         fields = ['departments']
#         ordering = ['created_time']
#         depth = 1


class ZipfileSerializer(serializers.ModelSerializer):
    zipfileid = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Zipfile
        fields = ['zipfile', 'zipfileid']
        read_only_fields = ['zipfileid']
        extra_kwargs = {
            'zipfile': {'write_only': True}
        }
        ref_name = 'couser_zipfile'
