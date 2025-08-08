from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data["product_id"]
            count = serializer.validated_data["count"]
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": "商品不存在。"}, status=status.HTTP_404_NOT_FOUND)
            if product.stock < count:
                return Response({"error": "庫存數量不足。"}, status=status.HTTP_400_BAD_REQUEST)
            cart = self.get_object()
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"count": count})
            if not created:
                # 如果商品已存在，增加數量
                new_count = cart_item.count + count
                if product.stock < new_count:
                    return Response({"error": "庫存數量不足。"}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.count = new_count
                cart_item.save()
            cart_serializer = CartSerializer(cart)
            return Response({"message": "商品已加入購物車。", "cart": cart_serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["patch"])
    def update_item(self, request):
        item_id = request.data.get("item_id")
        if not item_id:
            return Response({"error": "請提供商品ID。"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UpdateCartItemSerializer(data=request.data)
        if serializer.is_valid():
            count = serializer.validated_data["count"]
            try:
                cart = self.get_object()
                cart_item = cart.items.get(id=item_id)
                if count == 0:
                    cart_item.delete()
                    message = "商品已從購物車移除。"
                else:
                    if cart_item.product.stock < count:
                        return Response({"error": "庫存數量不足。"}, status=status.HTTP_400_BAD_REQUEST)
                    cart_item.count = count
                    cart_item.save()
                    message = "購物車已更新。"
                cart_serializer = CartSerializer(cart)
                return Response({"message": message, "cart": cart_serializer.data}, status=status.HTTP_200_OK)
            except CartItem.DoesNotExist:
                return Response({"error": "購物車商品不存在。"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        item_id = request.data.get("item_id")
        if not item_id:
            return Response({"error": "請提供商品ID。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart = self.get_object()
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()
            cart_serializer = CartSerializer(cart)
            return Response({"message": "商品已從購物車移除。", "cart": cart_serializer.data}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "購物車商品不存在。"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        cart_serializer = CartSerializer(cart)
        return Response({"message": "已清空購物車。", "cart": cart_serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def count(self, request):
        cart = self.get_object()
        return Response({"count": cart.total_items})
