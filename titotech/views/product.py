# titotech/views/product.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Max, Min, Sum, Count

from titotech.models              import Product
from titotech.serializers.product import ProductSerializer, ProductSummarySerializer
from titotech.permissions         import IsStaffOrReadOnly
from titotech.filters             import ProductFilter
from titotech.pagination          import StandardPagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset           = Product.objects.select_related('category').all()
    serializer_class   = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = ProductFilter
    search_fields      = ['brand', 'model', 'color', 'ram', 'category__name', 'compatibility']
    ordering_fields    = ['brand', 'model', 'price', 'stock', 'created_at', 'category__name']
    ordering           = ['category__name', 'brand', 'model']

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser],
        url_path='restock',
    )
    def restock(self, request, pk=None):
        """Agrega unidades al stock de un producto."""
        product = self.get_object()
        try:
            quantity = int(request.data.get('quantity', 0))
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'La cantidad debe ser un entero positivo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product.stock += quantity
        product.save(update_fields=['stock'])
        return Response({
            'id':          product.id,
            'producto':    str(product),
            'nuevo_stock': product.stock,
        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='disponibles',
    )
    def disponibles(self, request):
        """Lista todos los productos con stock disponible (sin autenticación)."""
        qs   = self.filter_queryset(
            self.get_queryset().filter(stock__gt=0, is_active=True)
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                ProductSummarySerializer(page, many=True).data
            )
        return Response(ProductSummarySerializer(qs, many=True).data)

    @action(
        detail=False,
        methods=['get'],
        url_path='stats',
    )
    def stats(self, request):
        """Estadísticas generales del inventario."""
        qs     = Product.objects.all()
        active = qs.filter(is_active=True)
        data   = active.aggregate(
            total_activos   = Count('id'),
            precio_promedio = Avg('price'),
            precio_max      = Max('price'),
            precio_min      = Min('price'),
            stock_total     = Sum('stock'),
        )
        data['total_inactivos'] = qs.filter(is_active=False).count()
        data['sin_stock']       = active.filter(stock=0).count()
        if data['precio_promedio']:
            data['precio_promedio'] = round(float(data['precio_promedio']), 2)

        # Por categoría
        por_categoria = (
            active
            .values('category__name')
            .annotate(total=Count('id'), stock=Sum('stock'))
            .order_by('category__name')
        )
        data['por_categoria'] = list(por_categoria)
        return Response(data)
