# apps/payment/admin.py - FIXED VERSION
from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'get_order_number',
        'user',
        'total_amount',
        'status',
        'esewa_status',
        'created_at',
        'get_order_status'
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
    
    # Custom methods for display
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
    
    # Custom actions
    actions = ['mark_as_success', 'mark_as_failed']
    
    def mark_as_success(self, request, queryset):
        updated = queryset.update(status='success')
        self.message_user(request, f'{updated} payment(s) marked as successful.')
    mark_as_success.short_description = "Mark selected payments as successful"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payment(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected payments as failed"
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    # Ordering
    ordering = ('-created_at',)
    
    # List per page
    list_per_page = 20