from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import UserGroupManagementViewSet,CartViewSet,MenuItemViewSet,OrderViewSet,manager,UserGroupViewSet

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menu-item')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('groups/manager/users/', UserGroupManagementViewSet.as_view({'get': 'list_managers', 'post': 'add_manager'})),
    path('groups/manager/users/<int:userId>/', UserGroupManagementViewSet.as_view({'delete': 'remove_manager'})),  
    path('groups/delivery-crew/users/', UserGroupManagementViewSet.as_view({'get': 'list_delivery_crew', 'post': 'add_delivery_crew'})),
    path('groups/delivery-crew/users/<int:userId>/', UserGroupManagementViewSet.as_view({'delete': 'remove_delivery_crew'})),
    path('cart/menu-items/', CartViewSet.as_view({'get': 'list_cart_items', 'post': 'add_to_cart', 'delete': 'clear_cart'})),
    path('api-token-auth',obtain_auth_token),
    path('users/<int:userid>/groups/',UserGroupViewSet.as_view({'post': 'add_to_group', 'delete': 'remove_from_group'})),
    path('manager',manager)
]

