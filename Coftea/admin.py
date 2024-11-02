from django.contrib import admin
from django.db import transaction
from .models import Category, Product, Inventory, OrderTransaction, OrderItem

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name')
    search_fields = ('category_name',)


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'price', 'category', 'quantity')
    search_fields = ('product_name',)
    list_filter = ('category',)


# Inventory Admin
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventory_id', 'product', 'quantity')
    search_fields = ('product__product_name',)


# OrderItem Inline (for displaying OrderItems within an OrderTransaction)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of extra blank items to display


# OrderTransaction Admin
@admin.register(OrderTransaction)
class OrderTransactionAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'transaction_date', 'total_price', 'paymentMethod', 'user')
    search_fields = ('user__username', 'order_id')
    list_filter = ('transaction_date',)
    inlines = [OrderItemInline]  # Adding OrderItem inline to display items within each order