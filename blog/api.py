from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from django_filters.rest_framework import DjangoFilterBackend
from permissions.permissions import RolePermission


class ArticleViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    renderer_classes = (EmberJSONRenderer,)
    queryset = Article.objects.all().order_by('-pub_time')
    serializer_class = ArticleSerializer
    parser_classes = (MultiPartParser,)
    pagination_class = ListPagination
    permission_classes = [RolePermission]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('status',)

    def get_object(self):

        instance = super(ArticleViewSet, self).get_object()
        instance.viewed()
        return instance

    def get_serializer_class(self):
        if self.action == 'bulkdel':
            return ArticleListSerializer
        return ArticleSerializer

    @action(detail=False, methods=['PATCH'], name='bulk delete articles')
    def bulkdel(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.deletearticles()

        return Response({})
