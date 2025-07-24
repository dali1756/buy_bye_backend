from rest_framework import viewsets, filters
from .models import Product, MainCategory, SubCategory
from .serializers import ProductSerializer, MainCategorySerializer, SubCategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

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

CategoryViewSet = MainCategoryViewSet
