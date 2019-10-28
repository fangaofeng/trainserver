from django.contrib import admin
from .models import Article
# Register your models here.
from imagekit.admin import AdminThumbnail


@admin.register(Article)
class ArticlelAdmin(admin.ModelAdmin):
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    list_per_page = 10
    search_fields = ('body', 'title')

    list_display = (
        'id', 'title', 'created', 'views', 'status', 'admin_thumbnail', 'article_order')
    list_display_links = ('id', 'title')

    exclude = ('created', 'modified')
    view_on_site = True
