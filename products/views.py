from rest_framework import viewsets, filters, status
from .models import Product, MainCategory, SubCategory, Brand
from .serializers import ProductSerializer, MainCategorySerializer, SubCategorySerializer, BrandSerializer, BrandList
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class MainCategoryViewSet(viewsets.ModelViewSet):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        queryset = SubCategory.objects.select_related("main_category")
        main_category = self.request.query_params.get("main_category", None)
        if main_category:
            queryset = queryset.filter(main_category__name=main_category)
        return queryset

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "main_category__name", "sub_category__name"]
    filterset_fields = {
        "main_category": ["exact"],
        "sub_category": ["exact"],
        "price": ["gte", "lte", "exact"],
        "stock": ["gte", "lte"],
    }
    ordering_fields = ["price", "name", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Product.objects.select_related("main_category", "sub_category")
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(main_category__name__icontains=search_query) | Q(sub_category__name__icontains=search_query))
        category_name = self.request.query_params.get("category_name", None)
        if category_name:
            queryset = queryset.filter(main_category__name=category_name)
        sub_category_name = self.request.query_params.get("sub_category_name", None)
        if sub_category_name:
            queryset = queryset.filter(sub_category__name=sub_category_name)
        min_price = self.request.query_params.get("min_price", None)
        max_price = self.request.query_params.get("max_price", None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

    @action(detail=False, methods=["get"])
    def search_suggestions(self, request):
        query = request.query_params.get("q", "")
        if len(query) < 2:
            return Response([])
        suggestions = Product.objects.filter(name__icontains=query).values_list("name", flat=True)[:5]
        return Response(list(suggestions))

@method_decorator(csrf_exempt, name="dispatch")
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "country", "description"]
    filterset_fields = {
        "is_active": ["exact"],
        "country": ["exact"],
    }
    ordering_fields = ["name", "sort_order", "created_at", "country"]
    ordering = ["sort_order", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return BrandList
        return BrandSerializer

    def get_queryset(self):
        queryset = Brand.objects.all()
        show_inactive = self.request.query_params.get("show_inactive", "false").lower()
        if show_inactive != "true":
            queryset = queryset.filter(is_active=True)
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(country__icontains=country)
        return queryset

    # 取得所有品牌國家
    @action(detail=False, methods=["get"])
    def countries(self, request):
        countries = Brand.objects.filter(is_active=True).values_list("country", flat=True).distinct().exclude(country__exact="")
        return Response(list(countries))

    # 取得指定品牌所有內容
    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        brand = self.get_object()
        products = brand.products.select_related("main_category", "sub_category")
        in_stock_only = request.query_params.get("in_stock_only", "false").lower()
        if in_stock_only == "true":
            products = products.filter(stock__gt=0)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    # 熱門商品，依照數量排序
    @action(detail=False, methods=["get"])
    def popular(self, request):
        brands = Brand.objects.filter(is_active=True).annotate(products_count=Count("products")).filter(products_count__gt=0).order_by("-products_count")[:10]
        serializer = BrandList(brands, many=True)
        return Response(serializer.data)

CategoryViewSet = MainCategoryViewSet
