from django.db import models

# Create your models here.


class Website_views(models.Model):
    """
    网站访问量统计表：字段ID、总访问量
    """

    views = models.IntegerField(default=0)
    name = models.CharField(max_length=20)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])
