# titotech/models/accessory.py
from django.db import models


class Accessory(models.Model):
    """
    Accesorios complementarios a los equipos móviles (estuches, cargadores, audífonos, etc.).
    Se puede asociar también a OrderItem para incluirlos en pedidos.
    """
    TYPE_CHOICES = [
        ('case',     'Estuche / Case'),
        ('charger',  'Cargador'),
        ('earphone', 'Audífonos'),
        ('cable',    'Cable'),
        ('screen',   'Protector de pantalla'),
        ('other',    'Otro'),
    ]

    name          = models.CharField(max_length=200, verbose_name='Nombre')
    type          = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='other',
        verbose_name='Tipo',
    )
    compatibility = models.TextField(
        blank=True,
        default='',
        verbose_name='Compatibilidad',
        help_text='Modelos de equipos compatibles (Ej: iPhone 15, Samsung S24)',
    )
    price         = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    stock         = models.PositiveIntegerField(default=0, verbose_name='Stock disponible')
    is_active     = models.BooleanField(default=True, verbose_name='Activo')
    image         = models.ImageField(
        upload_to='accessories/',
        blank=True,
        null=True,
        verbose_name='Imagen',
    )
    created_at    = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        ordering            = ['name']
        verbose_name        = 'Accesorio'
        verbose_name_plural = 'Accesorios'

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'

    @property
    def in_stock(self):
        return self.stock > 0
