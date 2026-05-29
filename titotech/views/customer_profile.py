# titotech/views/customer_profile.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from titotech.models              import CustomerProfile
from titotech.serializers.user    import CustomerProfileSerializer, CustomerProfileAdminSerializer
from titotech.pagination          import StandardPagination


class CustomerProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de perfiles de cliente.
    - Admin: acceso a todos los perfiles.
    - Cliente autenticado: solo accede a su propio perfil vía /users/profile/.
    """
    queryset           = CustomerProfile.objects.select_related('user').all()
    serializer_class   = CustomerProfileAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields      = ['user__username', 'user__email', 'city', 'phone_number']
    ordering_fields    = ['id', 'user__username', 'city']
    ordering           = ['id']

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()

