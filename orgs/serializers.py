# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError
from rest_framework import serializers  # , exceptions
from django.core.exceptions import ObjectDoesNotExist
import xlrd
from config.settings import base
from .models import Department, Excelfile

"""
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'parent', 'department_no')
        read_only_fields = ('created_time', 'department_no',)
        ordering = ['created_time']
"""


class RecursiveField(serializers.BaseSerializer):
    """
    Cria instancia do serializer parente e retorna os dados
    serializados.
    """

    def to_representation(self, value):
        ParentSerializer = self.parent.parent.__class__
        serializer = ParentSerializer(value, context=self.context)
        return serializer.data

    def to_internal_value(self, data):
        ParentSerializer = self.parent.parent.__class__
        Model = ParentSerializer.Meta.model
        try:
            instance = Model.objects.get(id=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Objeto {0} não encontrado".format(
                    Model().__class__.__name__
                )
            )
        return instance


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    slug = serializers.SlugField(write_only=True)
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


class ExcelfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Excelfile
        fields = ['excelfile']
        extra_kwargs = {
            'excelfile': {'write_only': True}
        }
