from django.contrib import admin

from .models import Category, MenuItem, Order, OrderItem, Restaurant, Table


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "customer_name", "status", "total", "created_at")
    list_filter = ("restaurant", "status")
    inlines = [OrderItemInline]


admin.site.register([Restaurant, Table, Category, MenuItem])
