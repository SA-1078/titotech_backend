# titotech/admin.py
from django.contrib import admin
from titotech.models import Category, Product, CustomerProfile, Order, OrderDetail


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'slug', 'is_active', 'created_at']
    list_filter   = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering      = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['id', 'category', 'brand', 'model', 'storage', 'color', 'price', 'stock', 'is_active']
    list_filter   = ['is_active', 'category', 'storage']
    search_fields = ['brand', 'model', 'color', 'compatibility']
    list_editable = ['price', 'stock', 'is_active']
    ordering      = ['category__name', 'brand', 'model']
    autocomplete_fields = ['category']


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'phone_number', 'city']
    search_fields = ['user__username', 'user__email', 'city']
    ordering      = ['user__username']


class OrderDetailInline(admin.TabularInline):
    model  = OrderDetail
    extra  = 0
    fields = ['product', 'quantity', 'unit_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ['id', 'customer', 'status', 'total_amount', 'created_at']
    list_filter     = ['status']
    search_fields   = ['customer__user__username']
    inlines         = [OrderDetailInline]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    ordering        = ['-created_at']
