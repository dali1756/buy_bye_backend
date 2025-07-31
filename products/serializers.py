from rest_framework import serializers
from .models import Product, MainCategory, SubCategory, Brand

class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = "__all__"

class SubCategorySerializer(serializers.ModelSerializer):
    main_category = MainCategorySerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    main_category = MainCategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_category(self, obj):
        if obj.main_category:
            return {
                "id": obj.main_category.id,
                "name": obj.main_category.name
            }
        return None

class BrandSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = "__all__"

    def get_products_count(self, obj):
        return obj.products.filter(stock__gt=0).count()

class BrandList(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    class Meta:
        model = Brand
        fields = "__all__"

    def get_products_count(self, obj):
        return obj.products.filter(stock__gt=0).count()

CategorySerializer = MainCategorySerializer
