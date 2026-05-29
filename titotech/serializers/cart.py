# titotech/serializers/cart.py
from rest_framework import serializers
from titotech.models.cart import Cart, CartItem
from titotech.models.product import Product
from titotech.serializers.product import ProductSummarySerializer


class CartItemSerializer(serializers.ModelSerializer):
    product  = ProductSummarySerializer(read_only=True)
    subtotal = serializers.FloatField(read_only=True)

    class Meta:
        model  = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal']
        read_only_fields = ['id', 'product', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items        = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.FloatField(read_only=True)
    num_items    = serializers.SerializerMethodField()

    class Meta:
        model  = Cart
        fields = ['id', 'total_amount', 'num_items', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_amount', 'num_items', 'items', 'created_at', 'updated_at']

    def get_num_items(self, obj):
        """Calcula el total de unidades de productos en el carrito."""
        return sum(item.quantity for item in obj.items.all())


class CartAddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity   = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        try:
            Product.objects.get(pk=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                f'El producto con ID {value} no existe o está inactivo.'
            )
        return value

    def validate(self, data):
        product  = Product.objects.get(pk=data['product_id'])
        quantity = data['quantity']
        
        # Validar si el stock disponible es suficiente
        if product.stock < quantity:
            raise serializers.ValidationError(
                f'Stock insuficiente del producto "{product.model}". Solo hay {product.stock} unidades disponibles.'
            )
        return data
