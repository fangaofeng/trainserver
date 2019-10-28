# from django.conf import settings
# from django.utils.http import urlsafe_base64_decode as uid_decoder
# from django.utils.translation import ugettext_lazy as _
# from django.utils.encoding import force_text
# from rest_framework.exceptions import ValidationError
from rest_framework import serializers  # , exceptions

from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'created_time', 'answer_user_id', 'unanswer', 'verb', 'title',
                  'ask_content', 'ask_time', 'answer_content', 'answer_time', 'position')
        read_only_fields = ('created_time', 'group_no',)
        ordering = ['created_time']
