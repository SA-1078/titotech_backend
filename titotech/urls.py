# titotech/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from titotech.views.health            import health_check
from titotech.views.auth              import RegisterView, LogoutView
from titotech.views.user              import UserViewSet
from titotech.views.category          import CategoryViewSet
from titotech.views.product           import ProductViewSet
from titotech.views.order             import OrderViewSet
from titotech.views.customer_profile  import CustomerProfileViewSet
from titotech.views.order_detail      import OrderDetailViewSet
from titotech.views.cart              import CartViewSet
from titotech.serializers.auth        import CustomTokenView

router = DefaultRouter()
router.register('users',            UserViewSet,            basename='user')
router.register('categories',       CategoryViewSet,        basename='category')
router.register('products',         ProductViewSet,         basename='product')
router.register('orders',           OrderViewSet,           basename='order')
router.register('customerprofiles', CustomerProfileViewSet, basename='customerprofile')
router.register('orderdetails',     OrderDetailViewSet,     basename='orderdetail')
router.register('cart',             CartViewSet,            basename='cart')

urlpatterns = [
    path('health/',             health_check),
    path('auth/register/',      RegisterView.as_view()),
    path('auth/login/',         CustomTokenView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/token/verify/',  TokenVerifyView.as_view()),
    path('auth/logout/',        LogoutView.as_view()),
    path('', include(router.urls)),
]
