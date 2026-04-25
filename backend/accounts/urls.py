from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    login_view,
    register_view,
    refresh_token_view,
    me_view,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/refresh/', refresh_token_view, name='refresh-token'),
    path('auth/me/', me_view, name='me'),

    path('', include(router.urls)),
]
