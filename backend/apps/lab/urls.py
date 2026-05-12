from rest_framework.routers import DefaultRouter

from .views import (
    LabTestCatalogViewSet,
    LabOrderViewSet,
    LabOrderItemViewSet,
    LabResultViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register(r'lab-tests', LabTestCatalogViewSet, basename='lab-test')
router.register(r'lab-orders', LabOrderViewSet, basename='lab-order')
router.register(r'lab-order-items', LabOrderItemViewSet, basename='lab-order-item')
router.register(r'lab-results', LabResultViewSet, basename='lab-result')

urlpatterns = router.urls
