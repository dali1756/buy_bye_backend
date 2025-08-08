from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product

class SimpleProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "description", "category"]

    def get_category(self, obj):
        if obj.main_category:
            return obj.main_category.name
        return ""

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    count = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "count", "subtotal", "created_at"]

    def get_count(self, obj):
        return obj.count

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total_items", "total_price", "created_at", "updated_at"]

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    count = serializers.IntegerField(default=1, min_value=1)

class UpdateCartItemSerializer(serializers.Serializer):
    count = serializers.IntegerField(min_value=0)
