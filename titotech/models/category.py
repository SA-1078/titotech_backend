# titotech/models/category.py
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Categorías para clasificar tanto equipos móviles como accesorios.
    Ej: Smartphones, Cases, Cargadores, Audífonos, Cables, Protectores.
    """
    name        = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    slug        = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, default='', verbose_name='Descripción')
    is_active   = models.BooleanField(default=True, verbose_name='Activo')
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        db_table            = 'titotech_categories'
        ordering            = ['name']
        verbose_name        = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
