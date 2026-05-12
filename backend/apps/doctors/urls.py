from rest_framework.routers import DefaultRouter

from .views import DoctorViewSet, SpecialtyViewSet

router = DefaultRouter()
router.register(r'specialties', SpecialtyViewSet, basename='specialty')
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns = router.urls
