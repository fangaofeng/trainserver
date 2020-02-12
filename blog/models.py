from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
# Create your models here.
from common.models import CreaterTimeStampedModel, TimeStampedModel
from django.contrib.auth import get_user_model


class Article(TimeStampedModel):
    """文章"""
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )
    COMMENT_STATUS = (
        ('o', '打开'),
        ('c', '关闭'),
    )
    ARTTYPE = (
        ('a', '文章'),
        ('p', '页面'),
    )
    title = models.CharField('标题', max_length=200)
    body = models.TextField('正文')
    description = models.CharField('描述', max_length=1000)
    pub_time = models.DateTimeField('发布时间', blank=True, null=True, default=timezone.now)
    status = models.CharField('文章状态', max_length=1, choices=STATUS_CHOICES, default='p')
    comment_status = models.CharField('评论状态', max_length=1, choices=COMMENT_STATUS, default='o')
    arttype = models.CharField('类型', max_length=1, choices=ARTTYPE, default='a')
    views = models.PositiveIntegerField('浏览量', default=0)
    article_order = models.IntegerField('排序,数字越大越靠前', blank=False, null=False, default=0)
    cover = models.ImageField(
        upload_to="blog/cover",  verbose_name=_('cover')
    )
    thumbnail = ImageSpecField(source='cover',
                               processors=[ResizeToFill(400, 300)],
                               format='JPEG',
                               options={'quality': 90})
    excerpt = models.CharField(max_length=200, blank=True)

    # created_time = models.DateTimeField('创建时间', default=timezone.now)
    # last_mod_time = models.DateTimeField('修改时间',  default=timezone.now)
    User = get_user_model()
    creater = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-article_order', '-pub_time']
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    # def get_absolute_url(self):
    #     return reverse('blog:detailbyid', kwargs={
    #         'article_id': self.id,
    #         'year': self.created_time.year,
    #         'month': self.created_time.month,
    #         'day': self.created_time.day
    #     })
    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])
