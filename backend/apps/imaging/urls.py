from rest_framework.routers import DefaultRouter

from .views import (
    ImagingTypeCatalogViewSet,
    ImagingOrderViewSet,
    ImagingReportViewSet,
    ImagingFileViewSet,
)

router = DefaultRouter()
router.register(r'imaging-types', ImagingTypeCatalogViewSet, basename='imaging-type')
router.register(r'imaging-orders', ImagingOrderViewSet, basename='imaging-order')
router.register(r'imaging-reports', ImagingReportViewSet, basename='imaging-report')
router.register(r'imaging-files', ImagingFileViewSet, basename='imaging-file')

urlpatterns = router.urls
