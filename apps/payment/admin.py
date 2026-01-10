# apps/payment/admin.py - VIEW-ONLY VERSION
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import PaymentTransaction
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

# ==================== PAYMENT TRANSACTION ADMIN ====================

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(ModelAdmin):
    list_display = (
        'get_order_number',
        'user',
        'total_amount',
        'status',
        'esewa_status',
        'created_at',
        'get_order_status',
    )
    
    list_filter = (
        'status',
        'esewa_status',
        'created_at',
        'user',
    )
    
    search_fields = (
        'order__order_number',
        'transaction_uuid',
        'user__username',
        'user__email',
        'reference_id',
    )
    
    readonly_fields = (
        'transaction_uuid',
        'user',
        'order',
        'amount',
        'tax_amount',
        'total_amount',
        'service_charge',
        'delivery_charge',
        'product_code',
        'signature',
        'status',
        'esewa_status',
        'reference_id',
        'created_at',
        'updated_at',
        'esewa_response_data',
        'get_order_link',
        'get_payment_details',
    )
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'transaction_uuid',
                'user',
                'order',
                'get_order_link',
                'status',
                'esewa_status',
                'reference_id',
            )
        }),
        ('Amount Details', {
            'fields': (
                'amount',
                'tax_amount',
                'total_amount',
                'service_charge',
                'delivery_charge',
                'get_payment_details',
            )
        }),
        ('eSewa Information', {
            'fields': (
                'product_code',
                'signature',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
        ('Response Data', {
            'fields': (
                'esewa_response_data',
            ),
            'classes': ('collapse',)
        }),
    )
    
    # ========== PERMISSION METHODS ==========
    
    def has_module_permission(self, request):
        """Both staff and owners can see this module"""
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Both staff and owners can view payment transactions"""
        return request.user.is_staff
    
    def has_add_permission(self, request):
        """No one can add payment transactions through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Staff can view but not edit.
        Owners can view but not edit (since fields are readonly anyway).
        """
        # Allow GET requests (viewing) for both staff and owners
        if request.method == 'GET':
            return request.user.is_staff
        # Disable POST requests (editing) for everyone since payments are readonly
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only owners can delete payment transactions"""
        return is_owner_user(request)
    
    # ========== ADMIN VIEW CUSTOMIZATIONS ==========
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Customize the change view based on user type"""
        extra_context = extra_context or {}
        
        # Check delete permission
        can_delete = self.has_delete_permission(request)
        
        extra_context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': can_delete,  # Only owners see delete button
            'title': f"View Payment Transaction #{object_id}",
            'is_readonly': True
        })
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def delete_view(self, request, object_id, extra_context=None):
        """Custom delete view with warning for owners"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Delete Payment Transaction'
        extra_context['warning_message'] = (
            '⚠️ WARNING: Deleting payment records removes audit trail. '
            'This action cannot be undone.'
        )
        
        return super().delete_view(request, object_id, extra_context)
    
    def get_readonly_fields(self, request, obj=None):
        """All fields are read-only for everyone"""
        if obj:  # If viewing an existing object
            return list(self.readonly_fields) + [
                'transaction_uuid', 'user', 'order', 'amount', 'tax_amount',
                'total_amount', 'service_charge', 'delivery_charge', 'product_code',
                'signature', 'status', 'esewa_status', 'reference_id', 'created_at',
                'updated_at', 'esewa_response_data'
            ]
        return super().get_readonly_fields(request, obj)
    
    # ========== LIST DISPLAY METHODS ==========
    
    def get_order_number(self, obj):
        return obj.order.order_number if obj.order else 'N/A'
    get_order_number.short_description = 'Order Number'
    get_order_number.admin_order_field = 'order__order_number'
    
    def get_order_status(self, obj):
        if obj.order:
            return obj.order.get_status_display()
        return 'N/A'
    get_order_status.short_description = 'Order Status'
    
    def get_order_link(self, obj):
        if obj.order:
            url = f"/admin/orders/order/{obj.order.id}/change/"
            return format_html('<a href="{}">View Order #{}</a>', url, obj.order.order_number)
        return 'No order linked'
    get_order_link.short_description = 'Order Link'
    
    def get_payment_details(self, obj):
        return format_html(
            '<strong>Subtotal:</strong> NPR {}<br>'
            '<strong>Tax:</strong> NPR {}<br>'
            '<strong>Service Charge:</strong> NPR {}<br>'
            '<strong>Delivery:</strong> NPR {}<br>'
            '<strong>Total:</strong> <span style="color: green; font-weight: bold;">NPR {}</span>',
            obj.amount,
            obj.tax_amount,
            obj.service_charge,
            obj.delivery_charge,
            obj.total_amount
        )
    get_payment_details.short_description = 'Payment Breakdown'
    
    # ========== CUSTOM ACTIONS ==========
    
    actions = ['mark_as_success', 'mark_as_failed']
    
    def get_actions(self, request):
        """Customize available actions based on user type"""
        actions = super().get_actions(request)
        
        if 'delete_selected' in actions:
            # Only show delete_selected for owners
            if not is_owner_user(request):
                del actions['delete_selected']
        
        # Remove custom actions for staff
        if is_staff_user(request):
            if 'mark_as_success' in actions:
                del actions['mark_as_success']
            if 'mark_as_failed' in actions:
                del actions['mark_as_failed']
        
        return actions
    
    def mark_as_success(self, request, queryset):
        """
        Only owners can mark payments as successful.
        This is useful for manual reconciliation.
        """
        if not is_owner_user(request):
            self.message_user(request, 'Only owners can modify payment status.', level='error')
            return
        
        updated = queryset.update(status='success')
        self.message_user(request, f'{updated} payment(s) marked as successful.')
    
    mark_as_success.short_description = "Mark selected payments as successful"
    mark_as_success.allowed_permissions = ('change',)
    
    def mark_as_failed(self, request, queryset):
        """
        Only owners can mark payments as failed.
        """
        if not is_owner_user(request):
            self.message_user(request, 'Only owners can modify payment status.', level='error')
            return
        
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payment(s) marked as failed.')
    
    mark_as_failed.short_description = "Mark selected payments as failed"
    mark_as_failed.allowed_permissions = ('change',)
    
    # ========== DELETE MODEL OVERRIDE ==========
    
    def delete_model(self, request, obj):
        """Custom delete with additional checks"""
        if not is_owner_user(request):
            messages.error(request, "Only owners can delete payment records.")
            return
        
        # Additional safety check
        if obj.status == 'success' and obj.order and obj.order.status in ['delivered', 'completed']:
            messages.error(
                request,
                f"Cannot delete payment #{obj.transaction_uuid}. "
                f"It's linked to completed order #{obj.order.order_number}."
            )
            return
        
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Bulk delete with checks"""
        if not is_owner_user(request):
            messages.error(request, "Only owners can delete payment records.")
            return
        
        # Filter out payments that shouldn't be deleted
        safe_to_delete = queryset.exclude(
            status='success',
            order__status__in=['delivered', 'completed']
        )
        
        unsafe_count = queryset.count() - safe_to_delete.count()
        
        if unsafe_count > 0:
            messages.error(
                request,
                f"Cannot delete {unsafe_count} payment(s) linked to completed orders."
            )
            return
        
        super().delete_queryset(request, safe_to_delete)
    
    # ========== ADMIN CONFIGURATION ==========
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Ordering
    ordering = ('-created_at',)
    
    # List per page
    list_per_page = 20
    
    # Optimize queryset
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'order'
        )