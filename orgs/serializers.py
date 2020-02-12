# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError
from rest_framework import serializers  # , exceptions
from django.core.exceptions import ObjectDoesNotExist
import xlrd
from config.settings import base
from rest_flex_fields import FlexFieldsModelSerializer
from .models import Department, Excelfile
from users.serializers import UserDetailsSerializer
from django.contrib.auth import get_user_model
from common.serializers import ADDDELSerializer
from rest_framework_recursive.fields import RecursiveField


class DepartmentSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'slug')
        read_only_fields = ('created_time', 'slug',)
        ordering = ['created_time']
        expandable_fields = {'trainmanager': (
            UserDetailsSerializer, {'source': 'trainmanager', "read_only": True})}

    def to_representation(self, value):
        ret = super().to_representation(value)
        if ret['parent'] is None:
            ret.pop('parent')
        return ret


class DepartmentWriteSerializer(serializers.ModelSerializer):

    # User = get_user_model()
    # trainmanager = serializers.PrimaryKeyRelatedField(
    #     required=False, many=True, queryset=User.objects.exclude(roles="系统管理员"))

    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'trainmanager')

    def validate(self, data):
        validat_data = super(DepartmentWriteSerializer, self).validate(data)
        parent = validat_data.get('parent', None)
        name = validat_data.get('name', None)
        if self.instance is None and name:
            if parent is None:
                validat_data['slug'] = name
            else:
                validat_data['slug'] = '/'.join([parent.slug, name])
        return validat_data

    def update(self, instance, validated_data):
        name = validated_data.pop('name', None)
        trainmanager = validated_data.pop('trainmanager', None)
        parent = validated_data.pop('parent', None)
        if name:
            instance.name = name
        if trainmanager:
            instance.trainmanager = trainmanager
        if parent:
            instance.move_to(parent)
        instance.clean()
        instance.save()
        return instance

    # def create(self, validated_data):
    #     tracks_data = validated_data.pop('tracks')
    #     album = Album.objects.create(**validated_data)
    #     for track_data in tracks_data:
    #         Track.objects.create(album=album, **track_data)
    #     return album


# class RecursiveField(serializers.BaseSerializer):
#     """
#     Cria instancia do serializer parente e retorna os dados
#     serializados.
#     """

#     def to_representation(self, value):
#         ParentSerializer = self.parent.parent.__class__
#         serializer = ParentSerializer(value, context=self.context)
#         return serializer.data

#     def to_internal_value(self, data):
#         ParentSerializer = self.parent.parent.__class__
#         Model = ParentSerializer.Meta.model
#         try:
#             instance = Model.objects.get(id=data)
#         except ObjectDoesNotExist:
#             raise serializers.ValidationError(
#                 "Objeto {0} no exist".format(
#                     Model().__class__.__name__
#                 )
#             )
#         return instance


class DepartmentRecursiveSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(required=False)
    # slug = serializers.SlugField(write_only=True)
    children = RecursiveField(many=True, required=False)

    class Meta:
        model = Department
        fields = ("id", "name", "children", "slug", "parent")

    def validate(self, data):
        name = data.get('name', None)

        children = data.get('children', None)

        if not name and not children:
            raise serializers.ValidationError("获取部门信息失败")
        return data

    def to_representation(self, value):
        ret = super().to_representation(value)
        if len(ret['children']) == 0:
            ret.pop('children')
        if ret['parent'] is None:
            ret.pop('parent')
        return ret


class ExcelfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Excelfile
        fields = ['excelfile']
        extra_kwargs = {
            'excelfile': {'write_only': True}
        }
