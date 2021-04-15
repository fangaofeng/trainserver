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
    path('auth/logout', LogoutView.as_view(), name='auth_logout'),
    path('account/info', AccountDetailView.as_view(), name='account_details'),
    path('account/avatar', UserAvatarView.as_view(), name='account_avatar'),

    path('user/upload', ExcelfileUploadView.as_view(), name='user_upload'),

]
urlpatterns += router.urls
