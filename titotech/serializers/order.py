# titotech/serializers/order.py
from rest_framework import serializers
from titotech.models import Order, OrderDetail, Product
from titotech.serializers.product import ProductSummarySerializer


class OrderDetailSerializer(serializers.ModelSerializer):
    product  = ProductSummarySerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model  = OrderDetail
        fields = ['id', 'product', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'unit_price']

    def get_subtotal(self, obj):
        return obj.subtotal


class OrderDetailAdminSerializer(serializers.ModelSerializer):
    product  = ProductSummarySerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model  = OrderDetail
        fields = ['id', 'order', 'product', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id', 'order', 'unit_price']

    def get_subtotal(self, obj):
        return obj.subtotal



class OrderSerializer(serializers.ModelSerializer):
    items          = OrderDetailSerializer(many=True, read_only=True)
    username       = serializers.CharField(source='customer.user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    num_items      = serializers.SerializerMethodField()

    class Meta:
        model  = Order
        fields = [
            'id', 'username', 'status', 'status_display',
            'total_amount', 'num_items', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

    def get_num_items(self, obj):
        return obj.items.count()


class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity   = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            Product.objects.get(pk=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                f'El producto {value} no existe o está inactivo.'
            )
        return value

    def validate(self, data):
        product = Product.objects.get(pk=data['product_id'])
        if product.stock < data['quantity']:
            raise serializers.ValidationError(
                f'Stock insuficiente: solo quedan {product.stock} unidades disponibles.'
            )
        return data
