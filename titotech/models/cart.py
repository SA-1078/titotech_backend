# titotech/models/cart.py
from django.db import models
from .customer_profile import CustomerProfile
from .product import Product


class Cart(models.Model):
    """
    Representa el carrito de compras temporal de un cliente.
    Tiene una relación OneToOne con CustomerProfile.
    """
    customer   = models.OneToOneField(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Cliente',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        db_table            = 'titotech_carts'
        verbose_name        = 'Carrito de Compras'
        verbose_name_plural = 'Carritos de Compras'

    def __str__(self):
        return f'Carrito de {self.customer.user.username}'

    @property
    def total_amount(self):
        """Calcula el total sumando el subtotal de cada ítem."""
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """
    Registra los productos agregados a un carrito de compras.
    """
    cart       = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrito',
    )
    product    = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Producto',
    )
    quantity   = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Agregado el')

    class Meta:
        db_table            = 'titotech_cartitems'
        verbose_name        = 'Ítem de Carrito'
        verbose_name_plural = 'Ítems de Carrito'
        unique_together     = ('cart', 'product')

    @property
    def subtotal(self):
        """Calcula el subtotal multiplicando cantidad por precio unitario actual."""
        return float(self.product.price) * self.quantity

    def __str__(self):
        return f'{self.quantity}x {self.product.model} en el {self.cart}'
