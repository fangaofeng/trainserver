from rest_framework import routers
from .api import ArticleViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'article', ArticleViewSet)

urlpatterns = router.urls
