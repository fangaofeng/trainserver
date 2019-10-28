
from rest_framework import serializers  # , exceptions
from .models import uploadfile


class UploadfileSerializer(serializers.ModelSerializer):
    fileid = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = uploadfile
        fields = ['file', 'fileid']
        read_only_fields = ['fileid']
