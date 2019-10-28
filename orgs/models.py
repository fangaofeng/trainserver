from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
# Department.getobject_slug('江苏万海龙/研发中心/测试部/交付团队')


class Department(MPTTModel):
    name = models.CharField('部门名称', max_length=150)
    parent = TreeForeignKey('self', verbose_name='上级部门', null=True, blank=True,
                               related_name='children', on_delete=models.CASCADE)
    slug = models.SlugField(blank=True,unique=True)




    @staticmethod
    def getobject_slug(slug):

        try:
            tdepartment=Department.objects.get(slug=slug)
            return tdepartment
        except ObjectDoesNotExist as e:
            return None

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = []
        else:
            ancestors = [i.slug for i in ancestors]
        slugs = []
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[:i + 1]))
        return slugs

    def clean(self):

        if self.slug is None or len(self.slug) == 0:
            if self.parent:
                self.slug = '/'.join([self.parent.slug,self.name])
            else:
                self.slug =self.name

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = "department"

    class MPTTMeta:
        parent_attr = 'parent'

    def __str__(self):
        return self.name
class Excelfile(models.Model):
    excelfile_dir = './orgs_excelfile/'
    excelfile = models.FileField(upload_to=excelfile_dir, blank=True)
    importcount = models.PositiveIntegerField(_('count of import user'), default=0,blank=False)
    class Meta:
        verbose_name = 'Excelfile'
        verbose_name_plural = "excelfile"
    class MPTTMeta:
        parent_attr = 'excelfile'

    def __str__(self):
        return str(self.id)