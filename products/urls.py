from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, MainCategoryViewSet, SubCategoryViewSet, BrandViewSet

app_name = "products"

router = DefaultRouter()
router.register(r"main-categories", MainCategoryViewSet, basename="main-category")
router.register(r"sub-categories", SubCategoryViewSet, basename="sub-category")
router.register(r"categories", MainCategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
