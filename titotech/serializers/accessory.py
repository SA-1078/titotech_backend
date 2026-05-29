# titotech/serializers/accessory.py
from rest_framework import serializers
from titotech.models import Accessory


class AccessorySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    in_stock     = serializers.SerializerMethodField()

    class Meta:
        model  = Accessory
        fields = [
            'id', 'name', 'type', 'type_display',
            'compatibility', 'price', 'stock', 'in_stock',
            'is_active', 'image', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

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
