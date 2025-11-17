from django.urls import URLPattern, URLResolver, path

from server.apps.users.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    EmployeeDetailView,
    EmployeeView,
    LogoutView,
    PasswordRecoveryAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        'api/auth/login',
        CookieTokenObtainPairView.as_view(),
        name='login',
    ),
    path(
        'api/auth/refresh',
        CookieTokenRefreshView.as_view(),
        name='token_refresh',
    ),
    path(
        'api/auth/logout',
        LogoutView.as_view(),
        name='logout',
    ),
    path(
        'api/employees',
        EmployeeView.as_view(),
        name='employee',
    ),
    path(
        'api/employees/<int:pk>',
        EmployeeDetailView.as_view(),
        name='employee-update',
    ),
    path(
        'api/password-recovery',
        PasswordRecoveryAPIView.as_view(),
        name='password-recovery',
    ),
]
