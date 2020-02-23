import xlrd
from common.jsonrender import EmberJSONRenderer
from common.pagination import ListPagination
from common.viewset import ListUpdateViewSet, RoleFilterMixViewSet
from config.settings import base
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django_filters.rest_framework import DjangoFilterBackend
# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
from orgs.models import Department
from permissions.filters import RoleFilterBackend
from permissions.permissions import RolePermission
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .app_settings import (
    JWTSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    TokenSerializer,
    UserDetailsSerializer,
    create_token
)
from .filter import IsManagerFilterBackend, IsOwnerFilterBackend
from .models import Excelfile, TokenModel, User
# from rest_framework import viewsets, generics
from .serializers import AccountInfoDetailsSerializer, ExcelfileSerializer, UserAvtarSerializer, UserListSerializer
from .utils import jwt_encode

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)


class ExcelfileUploadView(CreateAPIView):
    """
    上传导入部门的excel文件，文件后缀名：xlsx
    """
    permission_classes = [RolePermission]
    parser_classes = (MultiPartParser,)
    serializer_class = ExcelfileSerializer

    def create(self, request, *args, **kwargs):
        count, importid = self.importexcel()
        data = request.data
        data['importcount'] = count
        data['importid'] = importid
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # 重载response ，返回统一处理
        return Response({'status': 'ok', 'importcount': count, 'importid': importid},
                        status=status.HTTP_200_OK, headers=headers)

    def importexcel(self):
        """
        读取文件内容
        :param kwargs:
        :return:
        """

        workbook = xlrd.open_workbook(filename=None, file_contents=self.request.FILES['excelfile'].read())
        sheet = workbook.sheet_by_index(0)
        nrows = sheet.nrows
        ncols = sheet.ncols
        count = 0
        headers = [
            'user_no',  # 学员编号
            'name',  # '学员姓名'
            'username',  # "登录账号"
            'password',  # "登录密码"
            'department_id',  # "所属部门"
            'employee_position',  # "学员职务"
            'role',  # "学员类别"
            'info',  # "个性化信息"
            'TrainManager'  # "培训管辖部门"
        ]  # 用户表关键字
        user_list = []  # 用户信息列表
        # 读取表信息
        importid = timezone.now().strftime("%Y%m%d%H%M%S")
        for row in range(1, nrows):
            user_dic = {}
            for col in range(0, ncols):
                key = headers[col]
                user_dic[key] = sheet.cell_value(rowx=row, colx=col)
            if user_dic:
                user_list.append(user_dic)

        # 循环匹配表字段

        for cell in range(len(user_list)):
            # for header in headers
            user_no = user_list[cell][headers[0]]
            user_no = user_no.replace(' ', '')
            name = user_list[cell][headers[1]]
            username = user_list[cell][headers[2]]
            username = username.replace(' ', '')
            password = user_list[cell][headers[3]]
            # department_id = user_list[cell][headers[4]]
            employee_position = user_list[cell][headers[5]]
            if user_list[cell][headers[6]] == "学员":
                role = str(user_list[cell][headers[6]]).replace("学员", '2')
            elif user_list[cell][headers[6]] == "系统管理员":
                role = str(user_list[cell][headers[6]]).replace("系统管理员", '0')
            elif user_list[cell][headers[6]] == "培训管理员":
                role = str(user_list[cell][headers[6]]).replace("培训管理员", '1')
            info = user_list[cell][headers[7]]
            TrainManager = user_list[cell][headers[8]]

            if User.objects.filter(user_no=user_no) or User.objects.filter(username=username).exists():
                # 判断数据库中是否有相同字段，若有则列表下标+1跳过，如有需要可返回相同字段内容
                print(user_no, username)
                continue
            else:
                # 添加数据
                user = User(
                    user_no=user_no,
                    name=name,
                    username=username,

                    department=Department.objects.filter(slug=user_list[cell][headers[4]]).first(),

                    employee_position=employee_position,
                    role=role,
                    info=info,
                    importid=importid
                    # work_company=work_company

                )

                user.set_password(password)  # 密码转码
                user.save()
                count += 1
                # if role == '培训管理员':
                #     # administrator= User.id  # 去数据库查询到role=1的用户ID
                #     department = Department.objects.get(slug=TrainManager)
                #     department.trainmanager = user
                #     department.save()

        return count, importid


class LoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.
    Calls Django Auth login method to register User ID
    in Django session framework

    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key.
    """
    renderer_classes = (EmberJSONRenderer,)
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = TokenModel
    throttle_scope = 'login'

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):
            response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user,
                                      self.serializer)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:

            data = {
                'roles': self.user.roles,
                'key': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_responseerror(self):

        return Response({'status': 'error'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        successlogin = self.serializer.is_valid(raise_exception=False)
        if (successlogin):
            self.login()
            return self.get_response()
        else:
            return self.get_responseerror()


class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """

    permission_classes = (AllowAny,)
    """
    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)
    """

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        django_logout(request)

        return Response({"detail": _("Successfully logged out.")},
                        status=status.HTTP_200_OK)


class AccountDetailView(RetrieveUpdateAPIView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email

    Returns UserModel fields.
    """
    # roles_filterbackends = [IsOwnerFilterBackend]
    # filter_backends = [RoleFilterBackend]
    serializer_class = AccountInfoDetailsSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)
    renderer_classes = (EmberJSONRenderer,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        https://github.com/Tivix/django-rest-auth/issues/275
        """
        return get_user_model().objects.none()


class UserAvatarView(CreateAPIView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email

    Returns UserModel fields.
    """
    serializer_class = UserAvtarSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)
    renderer_classes = (EmberJSONRenderer,)

    def create(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        https://github.com/Tivix/django-rest-auth/issues/275
        """
        return get_user_model().objects.none()


# importid = openapi.Parameter('importid',
#                              in_=openapi.IN_QUERY,
#                              description='导入的批次id',
#                              type=openapi.TYPE_STRING)
# role = openapi.Parameter('role',
#                          in_=openapi.IN_QUERY,
#                          description='用户角色',
#                          type=openapi.TYPE_STRING)


# @method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[importid, role]))
class UserView(RoleFilterMixViewSet, ModelViewSet):

    """
        sysadmin
        trainmanager
        employee
        importid
    """
    roles_filterbackends = [IsManagerFilterBackend]

    renderer_classes = (EmberJSONRenderer,)
    serializer_class = UserDetailsSerializer
    permission_classes = [RolePermission]
    pagination_class = ListPagination
    queryset = get_user_model().objects.all()
    filter_backends = [RoleFilterBackend, DjangoFilterBackend]
    filterset_fields = ['importid', 'role']

    def get_serializer_class(self):
        if self.action == 'bulkdelete':
            return UserListSerializer
        return UserDetailsSerializer

    # def get_queryset(self):
    #     """
    #     sysadmin
    #     trainmanager
    #     employee
    #     importid
    #     """
    #     # 需要增加权限处理
    #     # EMPLOYEE_ROLE_CHOICES = {'系统管理员': 0, '培训管理员': 1, '学员': 2}
    #     role = self.request.query_params.get('role', None)
    #     # role = EMPLOYEE_ROLE_CHOICES.get(role, None)
    #     if role:
    #         queryset = get_user_model().objects.filter(roles__name=role)
    #     else:
    #         queryset = get_user_model().objects.all()
    #     importid = self.request.query_params.get('importid', None)
    #     if importid is not None:
    #         queryset = queryset.filter(importid=importid)
    #     return queryset

    @action(detail=False, methods=['PATCH'], name='bulk delete users')
    def bulkdelete(self, request, *args, **kwargs):
        """
        批量删除用户

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.deleteusers()

        return Response({'status': 'ok'})


class PasswordResetView(GenericAPIView):
    """
    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(GenericAPIView):
    """
    Password reset e-mail link is confirmed, therefore
    this resets the user's password.

    Accepts the following POST parameters: token, uid,
        new_password1, new_password2
    Returns the success/fail message.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password has been reset with the new password.")}
        )


class PasswordChangeView(GenericAPIView):
    """
    Calls Django Auth SetPasswordForm save method.

    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message.
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordChangeView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("New password has been saved.")})
