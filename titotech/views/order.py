# titotech/views/order.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from titotech.models import Order, Product, CustomerProfile
from titotech.serializers.order import OrderSerializer
from titotech.permissions import IsOwnerOrStaff
from titotech.filters import OrderFilter
from titotech.pagination import StandardPagination


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consultar y gestionar el historial de compras concluidas (Órdenes).
    - GET /api/orders/ -> Historial de compras (cliente ve las suyas / admin ve todas).
    - GET /api/orders/{id}/ -> Detalles de una orden con sus productos.
    - DELETE /api/orders/{id}/ -> Cancelar/eliminar un pedido (restaura el stock).
    - POST /api/orders/{id}/actualizar-estado/ -> (Admin) Cambia el estado del pedido.
    - GET /api/orders/stats/ -> (Admin) Estadísticas de facturación.
    """
    serializer_class   = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_class    = OrderFilter
    ordering_fields    = ['created_at', 'total_amount']
    ordering           = ['-created_at']
    http_method_names  = ['get', 'delete', 'post', 'head', 'options']  # POST is only used for custom actions

    def get_queryset(self):
        if self.request.user.is_staff:
            return (
                Order.objects
                .select_related('customer__user')
                .prefetch_related('items__product__category')
                .all()
            )
        try:
            customer = self.request.user.profile
        except CustomerProfile.DoesNotExist:
            return Order.objects.none()
        return (
            Order.objects
            .filter(customer=customer)
            .prefetch_related('items__product__category')
        )

    def destroy(self, request, *args, **kwargs):
        """
        Cancela y elimina un pedido.
        Restaurará automáticamente el stock de todos los productos de esta orden en el inventario.
        """
        from django.db import transaction
        order = self.get_object()
        
        # Un cliente común solo puede cancelar pedidos que no hayan sido enviados o entregados
        if not request.user.is_staff and order.status in ['shipped', 'delivered', 'cancelled']:
            return Response(
                {'error': 'No puedes cancelar un pedido que ya ha sido enviado, entregado o cancelado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        with transaction.atomic():
            for item in order.items.all():
                product = Product.objects.select_for_update().get(pk=item.product.pk)
                product.stock += item.quantity
                product.save(update_fields=['stock'])
            order.delete()
            
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser],
        url_path='actualizar-estado',
    )
    def actualizar_estado(self, request, pk=None):
        """Permite al administrador cambiar el estado del pedido (shipped, delivered, etc.)."""
        order          = self.get_object()
        new_status     = request.data.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return Response(
                {'error': f'Estado inválido. Opciones válidas: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = new_status
        order.save(update_fields=['status'])
        return Response(OrderSerializer(order).data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAdminUser],
        url_path='stats',
    )
    def stats(self, request):
        """Estadísticas generales de facturación y ventas (Admin)."""
        from django.db.models import Count, Sum
        qs     = Order.objects.all()
        totals = qs.aggregate(
            total_pedidos  = Count('id'),
            total_ingresos = Sum('total_amount'),
        )
        by_status = {
            label: qs.filter(status=code).count()
            for code, label in Order.STATUS_CHOICES
        }
        return Response({
            'total_pedidos':  totals['total_pedidos'],
            'total_ingresos': float(totals['total_ingresos'] or 0),
            'por_estado':     by_status,
        })
