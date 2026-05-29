# titotech/views/accessory.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from titotech.models              import Accessory
from titotech.serializers.accessory import AccessorySerializer
from titotech.permissions         import IsStaffOrReadOnly
from titotech.filters             import AccessoryFilter
from titotech.pagination          import StandardPagination


class AccessoryViewSet(viewsets.ModelViewSet):
    queryset           = Accessory.objects.all()
    serializer_class   = AccessorySerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class    = AccessoryFilter
    search_fields      = ['name', 'compatibility']
    ordering_fields    = ['name', 'price', 'stock', 'created_at']
    ordering           = ['name']

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser],
        url_path='restock',
    )
    def restock(self, request, pk=None):
        """Agrega unidades al stock de un accesorio."""
        accessory = self.get_object()
        try:
            quantity = int(request.data.get('quantity', 0))
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'La cantidad debe ser un entero positivo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        accessory.stock += quantity
        accessory.save(update_fields=['stock'])
        return Response({
            'id':          accessory.id,
            'accesorio':   str(accessory),
            'nuevo_stock': accessory.stock,
        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='disponibles',
    )
    def disponibles(self, request):
        """Lista accesorios disponibles sin autenticación."""
        qs   = self.filter_queryset(
            self.get_queryset().filter(stock__gt=0, is_active=True)
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                AccessorySerializer(page, many=True).data
            )
        return Response(AccessorySerializer(qs, many=True).data)
