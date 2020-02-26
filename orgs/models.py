from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
# Create your models here.
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
# Department.getobject_slug('江苏万海龙/研发中心/测试部/交付团队')
from django.contrib.auth import get_user_model


class DepartmentManager(TreeManager):
    def get_departmentbyUser(self, user):
        try:
            return self.filter(trainmanager=user)
        except Exception as e:
            return None

    def getobjectbyslug(self, slug):

        try:
            tdepartment = self.get(slug=slug)
            return tdepartment
        except ObjectDoesNotExist as e:
            return None


class Department(MPTTModel):
    name = models.CharField('部门名称', max_length=150)
    parent = TreeForeignKey('self', verbose_name='上级部门', null=True, blank=True,
                            related_name='children', on_delete=models.CASCADE, db_index=True)
    slug = models.CharField(blank=True, unique=True, max_length=512)
    User = get_user_model()
    trainmanager = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='managerdepartment',
    )
    objects = DepartmentManager()

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except Exception as e:
            ancestors = []
        else:
            ancestors = [i.slug for i in ancestors]
        slugs = []
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[:i + 1]))
        return slugs

    def clean(self):

        if self.parent:
            self.slug = '/'.join([self.parent.slug, self.name])
        else:
            self.slug = self.name

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
    importcount = models.PositiveIntegerField(_('count of import user'), default=0, blank=False)

    class Meta:
        verbose_name = 'Excelfile'
        verbose_name_plural = "excelfile"

    class MPTTMeta:
        parent_attr = 'excelfile'

    def __str__(self):
        return str(self.id)
