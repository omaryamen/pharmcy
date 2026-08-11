"""URL routing for Enterprise Goods Receipt & Receiving Management API."""

from rest_framework.routers import DefaultRouter

from apps.goods_receipt.api.views import GoodsReceiptViewSet

router = DefaultRouter()
router.register("goods-receipts", GoodsReceiptViewSet, basename="goods-receipt")

urlpatterns = router.urls
