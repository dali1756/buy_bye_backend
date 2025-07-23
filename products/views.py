from rest_framework import viewsets, filters
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_fields = {
        "category": ["exact"],
        "price": ["gte", "lte", "exact"],
        "stock": ["gte", "lte"],
    }
    order_fields = ["price", "name", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Product.objects.select_related("category")
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(category__name__icontains=search_query))
        category_name = self.request.query_params.get("category_name", None)
        if category_name:
            queryset = queryset.filter(category__name=category_name)
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