from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem
from unfold.admin import ModelAdmin

# ==================== PERMISSION HELPERS ====================

def is_owner_user(request):
    """Check if user is owner/superuser"""
    if hasattr(request.user, 'user_type'):
        return request.user.user_type == 'owner'
    return request.user.is_superuser

def is_staff_user(request):
    """Check if user is staff (not owner)"""
    if hasattr(request.user, 'user_type'):
        return request.user.user_type == 'staff'
    return False

# ==================== CART ITEM INLINE ====================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'added_at', 'total_price_display', 'stock_status_display']
    fields = ['product', 'quantity', 'total_price_display', 'stock_status_display', 'added_at']
    
    # Make inline completely read-only for everyone
    can_delete = False
    max_num = 0  # Prevent adding new items
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def total_price_display(self, obj):
        return f"Rs. {obj.total_price:.2f}"
    total_price_display.short_description = 'Total Price'
    
    def stock_status_display(self, obj):
        """Check if product is in stock"""
        if obj.product.in_stock:
            return format_html('<span style="color: green;">✓ In Stock</span>')
        else:
            return format_html('<span style="color: red;">✗ Out of Stock</span>')
    stock_status_display.short_description = 'Stock Status'

# ==================== CART ADMIN ====================

@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['user', 'item_count', 'total_price_display', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user', 'created_at', 'updated_at', 'total_price_display', 'item_count']
    inlines = [CartItemInline]
    list_per_page = 20
    
    # ========== PERMISSION METHODS ==========
    
    def has_module_permission(self, request):
        """Both staff and owners can see this module"""
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Both staff and owners can view carts"""
        return request.user.is_staff
    
    def has_add_permission(self, request):
        """No one can add carts through admin (carts are created via frontend)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Staff can view but not edit.
        Owners can view but not edit (since fields are readonly anyway).
        """
        # Allow GET requests (viewing) for both staff and owners
        if request.method == 'GET':
            return request.user.is_staff
        # Disable POST requests (editing) for everyone since carts are readonly
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only owners can delete carts"""
        if is_staff_user(request):
            return False
        return is_owner_user(request)
    
    # ========== ADMIN VIEW CUSTOMIZATIONS ==========
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Customize the change view based on user type"""
        extra_context = extra_context or {}
        
        # Check delete permission
        can_delete = self.has_delete_permission(request)
        
        extra_context.update({
            'show_save': False,  # No one can edit
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': can_delete,  # Only owners see delete button
            'title': f"View Cart #{object_id}",
            'is_readonly': True
        })
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def get_readonly_fields(self, request, obj=None):
        """All fields are read-only for everyone"""
        if obj:  # If viewing an existing object
            return list(self.readonly_fields) + ['user']
        return super().get_readonly_fields(request, obj)
    
    # Remove delete action for staff
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        if is_staff_user(request):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        
        return actions
    
    # ========== FIELDSETS AND DISPLAY METHODS ==========
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'created_at', 'updated_at')
        }),
        ('Cart Summary', {
            'fields': ('item_count', 'total_price_display'),
            'classes': ('collapse',)
        }),
    )
    
    def item_count(self, obj):
        return obj.total_items
    item_count.short_description = 'Total Items'
    
    def total_price_display(self, obj):
        return f"Rs. {obj.total_price:.2f}"
    total_price_display.short_description = 'Total Value'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetching"""
        return super().get_queryset(request).prefetch_related('items', 'items__product')

# ==================== CART ITEM ADMIN ====================

@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ['product', 'cart_user', 'quantity', 'unit_price_display', 
                    'total_price_display', 'stock_status', 'added_at']
    list_filter = ['added_at', 'product__category']
    search_fields = ['product__name', 'cart__user__username', 'cart__user__email']
    readonly_fields = ['cart', 'product', 'quantity', 'added_at', 'total_price_display', 
                      'unit_price_display', 'stock_status']
    list_per_page = 30
    
    # ========== PERMISSION METHODS ==========
    
    def has_module_permission(self, request):
        """Both staff and owners can see this module"""
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Both staff and owners can view cart items"""
        return request.user.is_staff
    
    def has_add_permission(self, request):
        """No one can add cart items through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Everyone can view but no one can edit cart items"""
        # Allow GET requests (viewing) for both staff and owners
        if request.method == 'GET':
            return request.user.is_staff
        # Disable POST requests (editing) for everyone
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No one can delete individual cart items through admin"""
        return False
    
    # ========== ADMIN VIEW CUSTOMIZATIONS ==========
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Customize the change view - view-only for everyone"""
        extra_context = extra_context or {}
        extra_context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False,  # No one can delete cart items individually
            'title': f"View Cart Item #{object_id}",
            'is_readonly': True
        })
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def get_readonly_fields(self, request, obj=None):
        """All fields are read-only for everyone"""
        if obj:  # If viewing an existing object
            return list(self.readonly_fields) + ['cart', 'product', 'quantity', 'added_at']
        return super().get_readonly_fields(request, obj)
    
    # Remove delete action for everyone
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    # ========== FIELDSETS AND DISPLAY METHODS ==========
    
    fieldsets = (
        ('Item Information', {
            'fields': ('cart', 'product', 'quantity', 'added_at')
        }),
        ('Pricing & Stock', {
            'fields': ('unit_price_display', 'total_price_display', 'stock_status'),
            'classes': ('collapse',)
        }),
    )
    
    def cart_user(self, obj):
        return obj.cart.user.username
    cart_user.short_description = 'User'
    cart_user.admin_order_field = 'cart__user__username'
    
    def unit_price_display(self, obj):
        return f"Rs. {obj.product.base_price:.2f}"
    unit_price_display.short_description = 'Unit Price'
    
    def total_price_display(self, obj):
        return f"Rs. {obj.total_price:.2f}"
    total_price_display.short_description = 'Total Price'
    
    def stock_status(self, obj):
        """Check if product is in stock"""
        if obj.product.in_stock:
            return format_html('<span style="color: green;">✓ In Stock</span>')
        else:
            return format_html('<span style="color: red;">✗ Out of Stock</span>')
    stock_status.short_description = 'Stock Status'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('product', 'cart', 'cart__user')