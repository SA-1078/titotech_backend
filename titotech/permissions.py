# titotech/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    """
    Lectura pública (GET/HEAD/OPTIONS) sin autenticación.
    Solo el staff puede crear, modificar o eliminar.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrStaff(BasePermission):
    """
    Solo el propietario del pedido o el staff pueden acceder al objeto.
    """
    def has_object_permission(self, request, view, obj):
        return obj.customer.user == request.user or request.user.is_staff
