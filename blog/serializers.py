
from rest_framework import serializers  # , exceptions
from .models import Article
from common.serializers import OwnerFieldSerializer
from common.selffield import ChoiceField


class ArticleSerializer(OwnerFieldSerializer):
    status = ChoiceField(choices=Article.STATUS_CHOICES, required=False)
    arttype = ChoiceField(choices=Article.ARTTYPE, required=False)
    comment_status = ChoiceField(choices=Article.COMMENT_STATUS, required=False)
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('id', 'modified', 'created', 'views', 'creater', 'thumbnail')
        ordering = ['pub_time', 'modified']
        extra_kwargs = {'description': {'required': False}}

class ArticleListSerializer(serializers.Serializer):

    articles = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=Article.objects.all())

    class Meta:
        fields = ['articles']

    def deletearticles(self):
        for article in self.validated_data['articles']:
            article.delete()
