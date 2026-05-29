# titotech/models/order.py
from django.db import models
from .customer_profile import CustomerProfile
from .product import Product


class Order(models.Model):
    """
    Registra la cabecera de la compra realizada por el cliente.
    Cada Order pertenece a un CustomerProfile.
    """
    STATUS_CHOICES = [
        ('pending',   'Pendiente'),
        ('paid',      'Pagado'),
        ('shipped',   'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]

    customer     = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Cliente',
    )
    status       = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado',
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Monto total',
    )
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de venta')
    updated_at   = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        db_table            = 'titotech_orders'
        ordering            = ['-created_at']
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.id} — {self.customer.user.username} ({self.get_status_display()})'

    def calculate_total(self):
        """Recalcula el monto total sumando todos los ítems del pedido."""
        self.total_amount = sum(
            item.unit_price * item.quantity
            for item in self.items.all()
        )
        self.save(update_fields=['total_amount'])


class OrderDetail(models.Model):
    """
    Detalle del pedido (antes OrderItem).
    Conecta productos con pedidos y guarda el precio histórico de venta.
    """
    order      = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido',
    )
    product    = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Producto',
    )
    quantity   = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario (histórico)',
    )

    class Meta:
        db_table            = 'titotech_orderdetails'
        verbose_name        = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    @property
    def subtotal(self):
        return float(self.unit_price) * self.quantity

    def __str__(self):
        return f'{self.quantity}x {self.product}'
