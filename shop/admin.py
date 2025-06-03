from django.contrib import admin
from django.db.models import F
from django.contrib.admin import SimpleListFilter
from .models import Product, Contact, Orders, OrderUpdate, Advertise, Table

# Custom Filter for Low Stock
class LowStockFilter(SimpleListFilter):
    title = 'Low Stock Status'  # Display name in the admin filter
    parameter_name = 'is_low_stock'  # Query parameter name

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Low Stock'),
            ('no', 'Sufficient Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(stock_quantity__lte=F('low_stock_threshold'))
        if self.value() == 'no':
            return queryset.filter(stock_quantity__gt=F('low_stock_threshold'))
        return queryset

# Custom Admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'subcategory', 'price', 'stock_quantity', 'low_stock_threshold', 'is_low_stock', 'pub_date')
    search_fields = ('product_name', 'category', 'subcategory')
    list_filter = ('category', 'subcategory', LowStockFilter)  # Use custom filter instead of 'is_low_stock'
    list_editable = ('stock_quantity', 'low_stock_threshold')  # Allow inline editing of stock fields
    list_per_page = 20  # Limit items per page for better usability

    def is_low_stock(self, obj):
        """Display a boolean indicating if the product is low on stock."""
        return obj.stock_quantity <= obj.low_stock_threshold

    is_low_stock.boolean = True  # Display as a boolean icon (green check/red cross)
    is_low_stock.short_description = 'Low Stock'

    def get_queryset(self, request):
        """Optionally filter for Drinks category or low stock."""
        qs = super().get_queryset(request)
        # Optionally: Filter for Drinks only (uncomment if needed)
        # qs = qs.filter(category="Drinks")
        return qs

# Custom Admin for Contact
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'timestamp')
    search_fields = ('name', 'email', 'phone')
    list_per_page = 20

# Custom Admin for Orders
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'userId', 'amount', 'address', 'phone', 'payment_method', 'timestamp')
    search_fields = ('order_id', 'userId', 'phone', 'payment_method')
    list_filter = ('payment_method', 'timestamp')
    list_per_page = 20

# Custom Admin for OrderUpdate
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'update_desc', 'timestamp')
    search_fields = ('order_id', 'update_desc')
    list_per_page = 20

# Custom Admin for Advertise
class AdvertiseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20

# Custom Admin for Table
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'status', 'amount')
    search_fields = ('number', 'status')
    list_filter = ('status',)
    list_per_page = 20

# Register models with custom admin configurations
admin.site.register(Product, ProductAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderUpdate, OrderUpdateAdmin)
admin.site.register(Advertise, AdvertiseAdmin)
admin.site.register(Table, TableAdmin)