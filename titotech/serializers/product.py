# titotech/serializers/product.py
from rest_framework import serializers
from titotech.models import Product, Category
from titotech.serializers.category import CategorySerializer


class ProductSummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para listas y referencias en pedidos."""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'brand', 'model', 'storage', 'color',
            'price', 'stock', 'is_active', 'category_name',
        ]


class ProductSerializer(serializers.ModelSerializer):
    category       = CategorySerializer(read_only=True)
    category_id    = serializers.PrimaryKeyRelatedField(
        source='category',
        write_only=True,
        queryset=Category.objects.filter(is_active=True),
    )
    price_with_tax = serializers.SerializerMethodField()
    in_stock       = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'category', 'category_id',
            'brand', 'model', 'storage', 'ram', 'color',
            'compatibility', 'price', 'price_with_tax',
            'stock', 'in_stock', 'is_active',
            'image', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_price_with_tax(self, obj):
        return obj.price_with_tax

    def get_in_stock(self, obj):
        return obj.in_stock

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value
