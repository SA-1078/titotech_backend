# titotech/models/product.py
from django.db import models
from .category import Category


class Product(models.Model):
    """
    Tabla unificada de productos TitoTech.
    Incluye tanto equipos móviles como accesorios (cases, cargadores, etc.).
    La categoría determina el tipo de producto.
    """
    STORAGE_CHOICES = [
        ('',      'N/A'),
        ('32GB',  '32 GB'),
        ('64GB',  '64 GB'),
        ('128GB', '128 GB'),
        ('256GB', '256 GB'),
        ('512GB', '512 GB'),
        ('1TB',   '1 TB'),
    ]

    category      = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Categoría',
    )
    brand         = models.CharField(max_length=100, blank=True, default='', verbose_name='Marca')
    model         = models.CharField(max_length=200, verbose_name='Modelo / Nombre')
    storage       = models.CharField(
        max_length=10,
        choices=STORAGE_CHOICES,
        blank=True,
        default='',
        verbose_name='Almacenamiento',
    )
    ram           = models.CharField(max_length=20, blank=True, default='', verbose_name='RAM')
    color         = models.CharField(max_length=80, blank=True, default='', verbose_name='Color')
    compatibility = models.TextField(
        blank=True,
        default='',
        verbose_name='Compatibilidad',
        help_text='Para accesorios: modelos compatibles. Ej: Samsung Galaxy S25, iPhone 15',
    )
    price         = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    stock         = models.PositiveIntegerField(default=0, verbose_name='Stock disponible')
    is_active     = models.BooleanField(default=True, verbose_name='Activo')
    image         = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Imagen (URL o ruta local)',
    )
    created_at    = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at    = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        db_table            = 'titotech_products'
        ordering            = ['category', 'brand', 'model']
        verbose_name        = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        if self.brand:
            return f'{self.brand} {self.model} {self.storage}'.strip()
        return self.model

    @property
    def price_with_tax(self):
        """Precio con IVA del 15% (Ecuador)."""
        return round(float(self.price) * 1.15, 2)

    @property
    def in_stock(self):
        return self.stock > 0
