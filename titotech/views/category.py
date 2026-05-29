# titotech/views/category.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from titotech.models               import Category
from titotech.serializers.category import CategorySerializer
from titotech.serializers.product  import ProductSummarySerializer
from titotech.permissions          import IsStaffOrReadOnly
from titotech.pagination           import StandardPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['is_active']
    search_fields      = ['name', 'description']
    ordering_fields    = ['name', 'created_at']
    ordering           = ['name']

    @action(detail=True, methods=['get'], url_path='products')
    def products(self, request, pk=None):
        """Lista los productos activos de esta categoría."""
        category = self.get_object()
        qs       = category.products.filter(is_active=True).order_by('brand', 'model')
        page     = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                ProductSummarySerializer(page, many=True).data
            )
        return Response(ProductSummarySerializer(qs, many=True).data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Estadísticas de categorías."""
        qs = Category.objects.annotate(num_products=Count('products', distinct=True))
        return Response({
            'total':    qs.count(),
            'activas':  qs.filter(is_active=True).count(),
            'inactivas': qs.filter(is_active=False).count(),
            'detalle': [
                {
                    'id':           c.id,
                    'nombre':       c.name,
                    'num_productos': c.num_products,
                    'activa':       c.is_active,
                }
                for c in qs.order_by('name')
            ],
        })
