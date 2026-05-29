# titotech/views/cart.py
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from titotech.models.cart import Cart, CartItem
from titotech.models.customer_profile import CustomerProfile
from titotech.models.product import Product
from titotech.models.order import Order, OrderDetail
from titotech.serializers.cart import CartSerializer, CartAddItemSerializer
from titotech.serializers.order import OrderSerializer


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar el carrito de compras temporal.
    - Operaciones reservadas para clientes autenticados.
    - GET /api/cart/ -> Ver carrito actual y sus subtotales.
    - POST /api/cart/add-item/ -> Agregar o incrementar cantidad de un producto.
    - PATCH /api/cart/items/{id}/ -> Editar cantidad de un ítem.
    - DELETE /api/cart/items/{id}/ -> Quitar un ítem del carrito.
    - DELETE /api/cart/clear/ -> Vaciar por completo el carrito.
    - POST /api/cart/checkout/ -> Comprar/pagar e iniciar la orden permanente.
    """
    permission_classes = [IsAuthenticated]

    def _get_or_create_cart(self, request):
        customer, _ = CustomerProfile.objects.get_or_create(user=request.user)
        cart, _ = Cart.objects.get_or_create(customer=customer)
        return cart

    def list(self, request):
        """Retorna el carrito de compras del cliente autenticado."""
        cart = self._get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add-item')
    def add_item(self, request):
        """Agrega un producto al carrito temporal."""
        cart = self._get_or_create_cart(request)
        serializer = CartAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        product = Product.objects.get(pk=product_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Si ya existía el ítem, validamos si la suma no supera el stock
            new_quantity = item.quantity + quantity
            if product.stock < new_quantity:
                return Response(
                    {'error': f'Stock insuficiente para agregar más unidades. Stock disponible: {product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity = new_quantity
            item.save(update_fields=['quantity'])

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['patch', 'delete'], url_path=r'items/(?P<item_id>\d+)')
    def item_detail(self, request, item_id=None):
        """Permite actualizar la cantidad de un ítem o removerlo del carrito."""
        cart = self._get_or_create_cart(request)
        
        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'El ítem indicado no existe en tu carrito de compras.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'PATCH':
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

            # Verificar stock
            if item.product.stock < new_quantity:
                return Response(
                    {'error': f'Stock insuficiente. Solo quedan {item.product.stock} unidades de este producto.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantity = new_quantity
            item.save(update_fields=['quantity'])
            return Response(CartSerializer(cart).data)

        elif request.method == 'DELETE':
            item.delete()
            return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        """Vacía por completo el carrito de compras."""
        cart = self._get_or_create_cart(request)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        Checkout / Pago:
        - Convierte el carrito temporal en una Orden definitiva y permanente.
        - Descuenta stock de forma transaccional y vacía el carrito.
        """
        cart = self._get_or_create_cart(request)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response(
                {'error': 'No se puede realizar checkout de un carrito de compras vacío.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Transacción atómica
        with transaction.atomic():
            # 1. Bloquear y validar stock para todos los productos en el carrito
            for item in cart_items:
                product = Product.objects.select_for_update().get(pk=item.product.pk)
                if product.stock < item.quantity:
                    return Response(
                        {
                            'error': (
                                f'Stock insuficiente para el producto "{product.model}". '
                                f'Quedan {product.stock} unidades y requieres {item.quantity}.'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 2. Crear la Orden permanente
            order = Order.objects.create(
                customer=cart.customer,
                status='paid',  # En este flujo directo, el checkout simula el pago exitoso inmediato
            )

            # 3. Crear los Detalles del Pedido y restar stock
            for item in cart_items:
                product = Product.objects.select_for_update().get(pk=item.product.pk)
                
                # Crear detalle permanente con el precio histórico actual
                OrderDetail.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    unit_price=product.price
                )

                # Descontar stock
                product.stock -= item.quantity
                product.save(update_fields=['stock'])

            # 4. Calcular y guardar el total de la orden
            order.calculate_total()

            # 5. Vaciar los ítems del carrito (los registros temporales se eliminan)
            cart_items.delete()

        # Retornar la orden confirmada recién creada
        order.refresh_from_db()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
