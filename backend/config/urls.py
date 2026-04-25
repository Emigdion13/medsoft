from django.urls import include, path

from apps.core.views import health_check

urlpatterns = [
    path('health/', health_check, name='health'),
    path('api/', include('accounts.urls')),
]
