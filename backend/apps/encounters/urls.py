from rest_framework.routers import DefaultRouter

from .views import EncounterViewSet, VitalSignViewSet

router = DefaultRouter()
router.register(r'encounters', EncounterViewSet, basename='encounter')
router.register(r'vitalsigns', VitalSignViewSet, basename='vitalsign')

urlpatterns = router.urls
