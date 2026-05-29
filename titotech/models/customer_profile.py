# titotech/models/customer_profile.py
from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    """
    Extiende el usuario de Django con datos específicos de envío y contacto.
    Relación OneToOne con el modelo User de Django.
    """
    user             = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario',
    )
    phone_number     = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Teléfono',
    )
    shipping_address = models.TextField(
        blank=True,
        default='',
        verbose_name='Dirección de envío',
    )
    city             = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Ciudad',
    )

    class Meta:
        verbose_name        = 'Perfil de Cliente'
        verbose_name_plural = 'Perfiles de Clientes'

    def __str__(self):
        return f'Perfil de {self.user.username}'
