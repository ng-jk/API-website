from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action,api_view,permission_classes
from django.contrib.auth.models import User, Group
from .models import menuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request):
        return request.user.groups.filter(name='Manager').exists()

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request):
        return request.user.groups.filter(name='Delivery crew').exists()

@permission_classes([IsAdminUser])
class UserGroupViewSet(viewsets.ViewSet):

    @action(detail=True, methods=['post'], url_path='groups')
    def add_to_group(self, request, pk=None):
        groupname = request.data['groupname']
        if not groupname:
            return Response({'error': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=pk)
            group = Group.objects.get(name=groupname)
            group.user_set.add(user)
            return Response({'status': f'User added to {groupname} group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='groups')
    def remove_from_group(self, request, pk=None):
        groupname = request.data['groupname']
        if not groupname:
            return Response({'error': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=pk)
            group = Group.objects.get(name=groupname)
            group.user_set.remove(user)
            return Response({'status': f'User removed from {groupname} group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes ([IsAdminUser])
def manager ( request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == 'POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
            return Response({"message": "ok"})
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = menuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['Customer', 'Delivery Crew', 'Manager']).exists():
            return super().list(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)


class UserGroupManagementViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list_managers(self, request):
        managers = User.objects.filter(groups__name='Manager')
        return Response([user.username for user in managers], status=status.HTTP_200_OK)

    def add_manager(self, request):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            group, created = Group.objects.get_or_create(name='Manager')
            user.groups.add(group)
            return Response({'status': 'User added to manager group'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def remove_manager(self, request, userId):
        try:
            user = User.objects.get(id=userId)
            group = Group.objects.get(name='Manager')
            user.groups.remove(group)
            return Response({'status': 'User removed from manager group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_delivery_crew(self, request):
        delivery_crew = User.objects.filter(groups__name='Delivery Crew')
        return Response([user.username for user in delivery_crew], status=status.HTTP_200_OK)

    def add_delivery_crew(self, request):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            group, created = Group.objects.get_or_create(name='Delivery Crew')
            user.groups.add(group)
            return Response({'status': 'User added to delivery crew group'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def remove_delivery_crew(self, request, userId):
        try:
            user = User.objects.get(id=userId)
            group = Group.objects.get(name='Delivery Crew')
            user.groups.remove(group)
            return Response({'status': 'User removed from delivery crew group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list_cart_items(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def add_to_cart(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def clear_cart(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Customer').exists():
            queryset = self.queryset.filter(user=request.user)
        elif request.user.groups.filter(name='Delivery Crew').exists():
            queryset = self.queryset.filter(delivery_crew=request.user)
        elif request.user.groups.filter(name='Manager').exists():
            queryset = self.queryset.all()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        order = self.get_object()
        if order.user == request.user or order.delivery_crew == request.user or request.user.groups.filter(name='Manager').exists():
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None):
        order = self.get_object()
        if request.user.groups.filter(name='Manager').exists():
            serializer = self.get_serializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.user.groups.filter(name='Delivery Crew').exists():
            if 'status' in request.data:
                order.status = request.data['status']
                order.save()
                return Response({'status': 'Order status updated'}, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        order = self.get_object()
        if request.user.groups.filter(name='Manager').exists():
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
