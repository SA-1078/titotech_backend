# titotech/views/order_detail.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from titotech.models import OrderDetail, Product
from titotech.serializers.order import OrderDetailAdminSerializer
from titotech.pagination import StandardPagination


class OrderDetailViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de detalles de pedidos (ítems).
    - Acceso exclusivo para administradores (IsAdminUser).
    - Edición (PATCH) y eliminación (DELETE) manejan de forma transaccional
      el stock de los productos e inventario, además de recalcular los montos de la orden.
    """
    queryset = OrderDetail.objects.select_related('order', 'product__category').all()
    serializer_class = OrderDetailAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order', 'product']
    search_fields = ['product__name', 'order__customer__user__username']
    ordering_fields = ['id', 'quantity', 'unit_price', 'order__id']
    ordering = ['id']
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def update(self, request, *args, **kwargs):
        if request.method != 'PATCH':
            return Response(
                {'error': 'Método no permitido. Use PATCH para modificar cantidades.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        
        instance = self.get_object()
        new_quantity = request.data.get('quantity')
        if new_quantity is None:
            return Response(
                {'error': 'El campo "quantity" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            new_quantity = int(new_quantity)
            if new_quantity <= 0:
                raise ValueError()
        except ValueError:
            return Response(
                {'error': 'La cantidad debe ser un entero mayor a 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=instance.product.pk)
            diff = new_quantity - instance.quantity
            if diff > 0:
                if product.stock < diff:
                    return Response(
                        {'error': f'Stock insuficiente: solo quedan {product.stock} unidades adicionales.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                product.stock -= diff
            elif diff < 0:
                product.stock += abs(diff)
                
            product.save(update_fields=['stock'])
            instance.quantity = new_quantity
            instance.save(update_fields=['quantity'])
            instance.order.calculate_total()
            
        # Recargar la instancia
        instance.refresh_from_db()
        return Response(self.get_serializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=instance.product.pk)
            product.stock += instance.quantity
            product.save(update_fields=['stock'])
            order = instance.order
            instance.delete()
            order.calculate_total()
        return Response(status=status.HTTP_204_NO_CONTENT)
