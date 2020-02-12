
from django.test import TestCase
from common.utils import get_admin_site


from ..inlineadmin import CheckboxInlineModelAdmin
from ..models import Role, RoleOperationshipWithFilter, Operation


class RoleOperationshipWithFilterInline(CheckboxInlineModelAdmin):

    model = RoleOperationshipWithFilter
    fk_name = 'role'


class InlineadminTestCase(TestCase):
    def setUp(self):
        super(InlineadminTestCase, self).setUp()
        self.testInline = RoleOperationshipWithFilterInline(Role, get_admin_site())
        kwargs = {"name": 'api_account_info_retrieve', "viewName": 'users.api.AccountDetailView',
                  "method": 'get', "path": '/api/account/info', "action": 'retrieve'}
        Operation(**kwargs).save()

    def test_get_unique_name(self):
        # self.testInline = RoleOperationshipWithFilterInline(Role, get_admin_site())

        self.assertTrue(self.testInline._get_unique_name() == 'operation')

    def test_get_unique_foreign_model(self):
        # self.testInline = RoleOperationshipWithFilterInline(Role, get_admin_site())

        model = self.testInline._get_unique_foreign_model()
        self.assertEqual(type(model), type(Operation))

    def test_get_max_num(self):

        number = self.testInline.get_max_num(request=None)
        self.assertEqual(number, 1)
