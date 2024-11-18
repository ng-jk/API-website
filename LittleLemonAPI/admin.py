from django.contrib import admin

# Register your models here.

from .models import OrderItem,Category,menuItem,Cart,Order

admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(menuItem)
admin.site.register(Cart)