from django.urls import include, path, re_path
from .api import (
    LoginView, LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView, UserListView, ExcelfileUploadView, UserAvatarView
)

urlpatterns = [
    # URLs that do not require a session or valid token
    path('auth/password/reset', PasswordResetView.as_view(),
         name='user_password_reset'),
    path('auth/password/reset/confirm', PasswordResetConfirmView.as_view(),
         name='user_password_reset_confirm'),
    path('auth/login', LoginView.as_view(), name='user_login'),
    # URLs that require a user to be logged in with a valid session / token.
    path('auth/logout', LogoutView.as_view(), name='user_logout'),
    path('user/info', UserDetailsView.as_view(), name='user_details'),
    path('user/avatar', UserAvatarView.as_view(), name='user_avatar'),
    #path('user/list/trainmanager', UserListView.as_view(), name='user_list'),
    path('user/excelupload', ExcelfileUploadView.as_view(), name='ExcelfileUploadView'),
    # path('user/list/trainmanager', UserListView.as_view({'get': 'list'}), name='user_trainmanagerlist'),
    path('user/list', UserListView.as_view({'get': 'list'}), name='user_listall'),
    # path('user/list/<str:role>', UserListView.as_view({'get': 'list'}), name='user_listrole'),
    path('auth/password/change', PasswordChangeView.as_view(),
         name='user_password_change'),
]
