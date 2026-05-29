# titotech/views/order.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from titotech.models             import Order, OrderDetail, Product, CustomerProfile
from titotech.serializers.order  import OrderSerializer, AddItemSerializer
from titotech.permissions        import IsOwnerOrStaff
from titotech.filters            import OrderFilter
from titotech.pagination         import StandardPagination


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class   = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_class    = OrderFilter
    ordering_fields    = ['created_at', 'total_amount']
    ordering           = ['-created_at']
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']

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

    def perform_create(self, serializer):
        customer = self.request.user.profile
        serializer.save(customer=customer)

    @action(detail=True, methods=['post'], url_path='agregar-item')
    def agregar_item(self, request, pk=None):
        """Agrega un producto al pedido (solo si está en estado pendiente)."""
        from django.db import transaction
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {'error': f'No se puede modificar un pedido con estado "{order.get_status_display()}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            product  = Product.objects.select_for_update().get(pk=serializer.validated_data['product_id'])
            quantity = serializer.validated_data['quantity']

            item, created = OrderDetail.objects.get_or_create(
                order=order,
                product=product,
                defaults={'unit_price': product.price, 'quantity': quantity},
            )
            if not created:
                item.quantity += quantity
                item.save(update_fields=['quantity'])

            product.stock -= quantity
            product.save(update_fields=['stock'])
            order.calculate_total()

        order.refresh_from_db()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], url_path='confirmar')
    def confirmar(self, request, pk=None):
        """Cambia el estado del pedido de 'pendiente' a 'pagado'."""
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {'error': 'Solo se pueden confirmar pedidos en estado Pendiente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not order.items.exists():
            return Response(
                {'error': 'No se puede confirmar un pedido sin ítems.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = 'paid'
        order.save(update_fields=['status'])
        return Response(OrderSerializer(order).data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser],
        url_path='actualizar-estado',
    )
    def actualizar_estado(self, request, pk=None):
        """Permite al administrador cambiar el estado del pedido."""
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
        """Estadísticas generales de ventas."""
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
