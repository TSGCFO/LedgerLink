from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, BoxPriceViewSet

router = DefaultRouter()
router.register(r'materials', MaterialViewSet)
router.register(r'box-prices', BoxPriceViewSet)

urlpatterns = router.urls
