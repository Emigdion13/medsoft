from rest_framework.routers import DefaultRouter

from .views import ClinicalNoteViewSet, DiagnosisViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r'clinical-notes', ClinicalNoteViewSet, basename='clinical-note')
router.register(r'diagnoses', DiagnosisViewSet, basename='diagnosis')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = router.urls
