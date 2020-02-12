from django.urls import include, path, re_path
from rest_framework import routers


from .api import (
    LoginView, LogoutView, AccountDetailView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView,  ExcelfileUploadView, UserAvatarView, UserView
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'user', UserView)

urlpatterns = [
    # URLs that do not require a session or valid token
    path('auth/password/reset', PasswordResetView.as_view(),
         name='user_password_reset'),
    path('auth/password/reset/confirm', PasswordResetConfirmView.as_view(),
         name='user_password_reset_confirm'),
    path('auth/password/change', PasswordChangeView.as_view(),
         name='user_password_change'),
    path('auth/login', LoginView.as_view(), name='user_login'),
    # URLs that require a user to be logged in with a valid session / token.
    path('auth/logout', LogoutView.as_view(), name='auth_logout'),
    path('account/info', AccountDetailView.as_view(), name='account_details'),
    path('account/avatar', UserAvatarView.as_view(), name='account_avatar'),
    # path('user/list/trainmanager', UserListView.as_view(), name='user_list'),
    path('user/upload', ExcelfileUploadView.as_view(), name='user_upload'),
    # path('user/list/trainmanager', UserListView.as_view({'get': 'list'}), name='user_trainmanagerlist'),
    # path('user/list', UserListView.as_view({'get': 'list', 'patch': 'bulkdelete'}), name='user_list'),
    # path('user/list/<str:roles>', UserListView.as_view({'get': 'list'}), name='user_listrole'),

]
urlpatterns += router.urls
