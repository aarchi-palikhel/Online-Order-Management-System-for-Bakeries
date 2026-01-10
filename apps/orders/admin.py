from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from decimal import Decimal
from .models import Order, OrderItem, CakeDesignReference, SuccessfulOrders
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render


class CakeDesignReferenceInline(admin.TabularInline):
    """Inline for cake design references in OrderItem"""
    model = CakeDesignReference
    extra = 0
    max_num = 5
    readonly_fields = ['uploaded_at', 'design_image_preview', 'order_info']
    fields = ['title', 'image', 'design_image_preview', 'description', 'uploaded_at', 'order_info']
    
    def design_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    design_image_preview.short_description = 'Preview'
    
    def order_info(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
        return "No order"
    order_info.short_description = 'Order'


class OrderItemInline(admin.TabularInline):
    """Inline for order items in Order"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price_display', 'is_cake_display', 'cake_details']
    fields = ['product', 'quantity', 'price', 'total_price_display', 
              'is_cake_display', 'cake_details']
    
    def total_price_display(self, obj):
        return f"Rs. {obj.total_price:.2f}"
    total_price_display.short_description = 'Total'
    
    def is_cake_display(self, obj):
        if obj.is_cake:
            return format_html('<span style="color: green;">✓ Cake</span>')
        return format_html('<span style="color: gray;">Regular</span>')
    is_cake_display.short_description = 'Type'
    
    def cake_details(self, obj):
        if obj.is_cake:
            details = []
            if obj.cake_flavor:
                details.append(f"Flavor: {obj.display_flavor}")
            if obj.cake_weight:
                details.append(f"Weight: {obj.display_weight}")
            if obj.cake_tiers:
                details.append(f"Tiers: {obj.cake_tiers}")
            if obj.message_on_cake:
                details.append(f"Message: {obj.message_on_cake}")
            if obj.delivery_date:
                details.append(f"Delivery: {obj.delivery_date}")
            return format_html('<br>'.join(details))
        return "—"
    cake_details.short_description = 'Cake Customization'
    
    def has_add_permission(self, request, obj=None):
        # Prevent adding items directly
        return False


@admin.register(Order)
class OrderAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['order_id_display', 'order_number', 'user_info', 'total_amount_display', 
                    'status_display', 'payment_method_display', 'payment_status_display',
                    'delivery_type_display', 'item_count', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'delivery_type', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 
                     'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'total_amount_display',
                      'item_count_display', 'order_link', 'user_info_display',
                      'subtotal_display', 'delivery_fee_display', 'payment_status_display']
    inlines = [OrderItemInline]
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    # Add custom admin actions for order status updates
    actions = [
        'mark_as_paid', 
        'mark_as_confirmed', 
        'mark_as_baking', 
        'mark_as_ready', 
        'mark_as_completed', 
        'mark_as_cancelled'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_link', 'order_number', 'user_info_display', 'status', 
                      'delivery_type', 'item_count_display')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_status', 'payment_transaction'),
            'classes': ('collapse',)
        }),
        ('Amount Breakdown', {
            'fields': ('subtotal_display', 'delivery_fee_display', 'total_amount_display'),
            'classes': ('collapse',)
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'phone_number', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('successful-orders/', self.admin_site.admin_view(self.successful_orders_view),
                 name='orders_successful_orders'),
        ]
        return custom_urls + urls
    
    def order_id_display(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    order_id_display.short_description = 'ID'
    order_id_display.admin_order_field = 'id'
    
    def user_info(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_info.short_description = 'Customer'
    user_info.admin_order_field = 'user__username'
    
    def user_info_display(self, obj):
        user = obj.user
        info = [
            f"<strong>Username:</strong> {user.username}",
            f"<strong>Email:</strong> {user.email}",
            f"<strong>Phone:</strong> {obj.phone_number or 'Not provided'}",
        ]
        if user.first_name or user.last_name:
            info.insert(1, f"<strong>Name:</strong> {user.first_name} {user.last_name}".strip())
        
        url = reverse('admin:users_customuser_change', args=[user.id])
        info.append(f'<a href="{url}" class="button">View Customer Details</a>')
        return mark_safe('<br>'.join(info))
    user_info_display.short_description = 'Customer Information'
    
    def total_amount_display(self, obj):
        return f"Rs. {obj.total_amount:.2f}"
    total_amount_display.short_description = 'Total Amount'
    
    def status_display(self, obj):
        return format_html(
            '<span class="px-2 py-1 rounded text-xs font-bold {}">{}</span>',
            obj.get_status_display_class,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def payment_method_display(self, obj):
        payment_colors = {
            'cod': 'bg-blue-100 text-blue-800',
            'esewa': 'bg-green-100 text-green-800',
            'online': 'bg-green-100 text-green-800',
            'card': 'bg-purple-100 text-purple-800',
        }
        color_class = payment_colors.get(obj.payment_method, 'bg-gray-100 text-gray-800')
        return format_html(
            '<span class="px-2 py-1 rounded text-xs font-bold {}">{}</span>',
            color_class,
            obj.get_payment_method_display()
        )
    payment_method_display.short_description = 'Payment Method'
    
    def payment_status_display(self, obj):
        return format_html(
            '<span class="px-2 py-1 rounded text-xs font-bold {}">{}</span>',
            obj.get_payment_status_display_class,
            obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'Payment Status'
    
    def delivery_type_display(self, obj):
        delivery_colors = {
            'delivery': 'bg-blue-100 text-blue-800',
            'pickup': 'bg-orange-100 text-orange-800',
        }
        color_class = delivery_colors.get(obj.delivery_type, 'bg-gray-100 text-gray-800')
        # Get display value from DELIVERY_CHOICES
        delivery_choices_dict = dict(obj.DELIVERY_CHOICES)
        display_value = delivery_choices_dict.get(obj.delivery_type, obj.delivery_type)
        return format_html(
            '<span class="px-2 py-1 rounded text-xs font-bold {}">{}</span>',
            color_class,
            display_value
        )
    delivery_type_display.short_description = 'Delivery Type'
    
    def item_count_display(self, obj):
        return obj.item_count
    item_count_display.short_description = 'Total Items'
    
    def subtotal_display(self, obj):
        return f"Rs. {obj.subtotal:.2f}"
    subtotal_display.short_description = 'Subtotal (before delivery)'
    
    def delivery_fee_display(self, obj):
        return f"Rs. {obj.delivery_fee:.2f}"
    delivery_fee_display.short_description = 'Delivery Fee'
    
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.id])
        return format_html('<a href="{}">Edit Order #{}</a>', url, obj.id)
    order_link.short_description = 'Order'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'payment_transaction').prefetch_related('items', 'items__product')
    
    def has_add_permission(self, request):
        # Orders should be created through checkout process, not manually in admin
        return False
    
    # Custom admin actions for order status updates
    
    def mark_as_paid(self, request, queryset):
        """Mark selected orders as paid - THIS ADDS TO REVENUE"""
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f"✅ {updated} order(s) marked as paid. These orders are now counted as revenue.")
    mark_as_paid.short_description = "✅ Mark as paid"
    
    def mark_as_confirmed(self, request, queryset):
        """Mark selected orders as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"✅ {updated} order(s) marked as confirmed.")
    mark_as_confirmed.short_description = "📋 Mark as confirmed"
    
    def mark_as_baking(self, request, queryset):
        """Mark selected orders as baking"""
        updated = queryset.update(status='baking')
        self.message_user(request, f"✅ {updated} order(s) marked as baking.")
    mark_as_baking.short_description = "👨‍🍳 Mark as baking"
    
    def mark_as_ready(self, request, queryset):
        """Mark selected orders as ready for pickup"""
        updated = queryset.update(status='ready')
        self.message_user(request, f"✅ {updated} order(s) marked as ready for pickup.")
    mark_as_ready.short_description = "📦 Mark as ready for pickup"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected orders as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f"✅ {updated} order(s) marked as completed.")
    mark_as_completed.short_description = "🏁 Mark as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected orders as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"❌ {updated} order(s) marked as cancelled.")
    mark_as_cancelled.short_description = "❌ Mark as cancelled"
    
    def successful_orders_view(self, request):
        """
        Custom view to display successful orders statistics
        """
        # Get date range from request or use default
        days_param = request.GET.get('days', '30')
        try:
            days = int(days_param)
        except ValueError:
            days = 30
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get summary report
        summary = SuccessfulOrders.get_summary_report(start_date, end_date)
        
        # Get top products
        top_products = SuccessfulOrders.get_top_products(start_date, end_date, limit=10)
        
        # Get daily revenue
        daily_revenue = SuccessfulOrders.get_revenue_by_date_range(days)
        
        # Calculate percentage change if we have previous period data
        prev_end_date = start_date
        prev_start_date = prev_end_date - timedelta(days=days)
        prev_summary = SuccessfulOrders.get_summary_report(prev_start_date, prev_end_date)
        
        # Calculate percentage changes
        revenue_change = 0
        order_change = 0
        if prev_summary['total_revenue'] > 0:
            revenue_change = ((summary['total_revenue'] - prev_summary['total_revenue']) / prev_summary['total_revenue']) * 100
        
        if prev_summary['order_count'] > 0:
            order_change = ((summary['order_count'] - prev_summary['order_count']) / prev_summary['order_count']) * 100
        
        # Build the HTML content for the dashboard
        content = f"""
        <div style="max-width: 1200px; margin: 0 auto;">
            <h1>Successful Orders Dashboard</h1>
            <p>Showing data for the last {days} days ({start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')})</p>
            
            <div style="margin-bottom: 20px;">
                <form method="get" style="display: inline;">
                    <label for="days">View data for last:</label>
                    <select name="days" id="days" onchange="this.form.submit()">
                        <option value="7" {'selected' if days == 7 else ''}>7 days</option>
                        <option value="30" {'selected' if days == 30 else ''}>30 days</option>
                        <option value="90" {'selected' if days == 90 else ''}>90 days</option>
                        <option value="365" {'selected' if days == 365 else ''}>1 year</option>
                    </select>
                </form>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Total Revenue</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #4CAF50; margin: 10px 0;">Rs. {summary['total_revenue']:,.2f}</div>
                    <div style="color: #666; font-size: 0.9em;">From {summary['order_count']} successful orders</div>
                </div>
                
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Average Order Value</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #4CAF50; margin: 10px 0;">Rs. {summary['average_order_value']:,.2f}</div>
                    <div style="color: #666; font-size: 0.9em;">Per successful order</div>
                </div>
                
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Items Sold</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #4CAF50; margin: 10px 0;">{summary['total_items_sold']}</div>
                    <div style="color: #666; font-size: 0.9em;">Total products sold</div>
                </div>
                
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3>Delivery Types</h3>
        """
        
        for type_name, count in summary['delivery_types'].items():
            content += f'<div style="margin: 5px 0;"><strong>{type_name.title()}:</strong> {count} orders</div>'
        
        content += """
                </div>
            </div>
            
            <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px;">
                <h3>Top Selling Products (Last {days} days)</h3>
        """
        
        if top_products:
            content += """
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; background: #f5f5f5; font-weight: bold;">Product</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; background: #f5f5f5; font-weight: bold;">Quantity Sold</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; background: #f5f5f5; font-weight: bold;">Revenue</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; background: #f5f5f5; font-weight: bold;">Orders</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for product in top_products:
                content += f"""
                        <tr>
                            <td style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0;">{product['product_name']}</td>
                            <td style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0;">{product['quantity_sold']}</td>
                            <td style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0;">
                                <span style="background-color: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;">Rs. {product['revenue']:,.2f}</span>
                            </td>
                            <td style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0;">{product['orders_count']}</td>
                        </tr>
                """
            
            content += """
                    </tbody>
                </table>
            """
        else:
            content += "<p>No product sales data available.</p>"
        
        content += """
            </div>
            
            <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px;">
                <h3>Daily Revenue Trend (Last {days} days)</h3>
        """
        
        if daily_revenue:
            content += """
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; background: #f5f5f5; font-weight: bold;">Date</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; background: #f5f5f5; font-weight: bold;">Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for date, revenue in sorted(daily_revenue.items(), reverse=True):
                content += f"""
                        <tr>
                            <td style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0;">{date}</td>
                            <td style="padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0;">
                                <span style="background-color: #4CAF50; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;">Rs. {revenue:,.2f}</span>
                            </td>
                        </tr>
                """
            
            content += """
                    </tbody>
                </table>
            """
        else:
            content += "<p>No daily revenue data available.</p>"
        
        content += """
            </div>
            
            <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px;">
                <h3>About Successful Orders</h3>
                <p>Successful orders are defined as orders that meet <strong>ALL</strong> of these conditions:</p>
                <ul>
                    <li>✅ Payment Status: <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; background: #d4edda; color: #155724;">Paid</span></li>
                    <li>✅ Order Status: One of <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; background: #fff3cd; color: #856404;">Confirmed</span>, <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; background: #e2e3e5; color: #383d41;">Baking</span>, or <span style="display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; background: #d1ecf1; color: #0c5460;">Completed</span></li>
                </ul>
                <p><em>Note: Orders with status "pending", "ready", or "cancelled" are not considered successful, even if paid.</em></p>
            </div>
        </div>
        """
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Successful Orders Dashboard',
            'content': mark_safe(content),
        }
        
        return render(request, 'admin/base_site.html', context)


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['id_display', 'order_info', 'product_info', 'quantity', 
                    'price_display', 'total_price_display', 'is_cake_display', 
                    'created_at']
    list_filter = ['product__is_cake', 'product__category', 'created_at']
    search_fields = ['order__order_number', 'product__name', 'order__user__username']
    readonly_fields = ['total_price_display', 'order_link', 'product_link', 
                      'cake_details_display', 'created_at_display']
    inlines = [CakeDesignReferenceInline]
    list_per_page = 30
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_link', 'product_link', 'quantity', 'price', 'total_price_display')
        }),
        ('Cake Customization', {
            'fields': ('is_cake_display', 'cake_flavor', 'cake_custom_flavor', 
                      'cake_weight', 'cake_custom_weight', 'cake_tiers', 
                      'message_on_cake', 'delivery_date', 'special_instructions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at_display', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def id_display(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    id_display.short_description = 'ID'
    id_display.admin_order_field = 'id'
    
    def order_info(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html(
            '<a href="{}">Order #{}</a><br><small>{}</small>',
            url, obj.order.id, obj.order.order_number
        )
    order_info.short_description = 'Order'
    order_info.admin_order_field = 'order__id'
    
    def product_info(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html(
            '<a href="{}">{}</a><br><small>{}</small>',
            url, obj.product.name, obj.product.category.name
        )
    product_info.short_description = 'Product'
    
    def price_display(self, obj):
        return f"Rs. {obj.price:.2f}"
    price_display.short_description = 'Unit Price'
    
    def total_price_display(self, obj):
        return f"Rs. {obj.total_price:.2f}"
    total_price_display.short_description = 'Total Price'
    
    def is_cake_display(self, obj):
        if obj.is_cake:
            return format_html('<span style="color: green; font-weight: bold;">🎂 CAKE</span>')
        return format_html('<span style="color: gray;">Regular Item</span>')
    is_cake_display.short_description = 'Product Type'
    
    def cake_details_display(self, obj):
        if obj.is_cake:
            details = []
            if obj.cake_flavor:
                flavor = obj.display_flavor
                details.append(f"<strong>Flavor:</strong> {flavor}")
            if obj.cake_weight:
                weight = obj.display_weight
                details.append(f"<strong>Weight:</strong> {weight}")
            if obj.cake_tiers:
                details.append(f"<strong>Tiers:</strong> {obj.cake_tiers}")
            if obj.message_on_cake:
                details.append(f"<strong>Message:</strong> {obj.message_on_cake}")
            if obj.delivery_date:
                details.append(f"<strong>Delivery Date:</strong> {obj.delivery_date}")
            if obj.special_instructions:
                details.append(f"<strong>Instructions:</strong> {obj.special_instructions}")
            
            if details:
                return mark_safe('<br>'.join(details))
        return format_html('<span style="color: gray; font-style: italic;">No customization</span>')
    cake_details_display.short_description = 'Customization Details'
    
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html(
            '<a href="{}">Order #{}</a> ({})',
            url, obj.order.id, obj.order.order_number
        )
    order_link.short_description = 'Parent Order'
    
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_display.short_description = 'Created At'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'product', 'product__category', 'order__user'
        )
    
    def has_add_permission(self, request):
        # Order items should be created through order process
        return False


@admin.register(CakeDesignReference)
class CakeDesignReferenceAdmin(ModelAdmin):
    list_display = ['id_display', 'order_info', 'product_info', 'title', 
                    'image_preview', 'uploaded_at']
    list_filter = ['uploaded_at', 'order__status']
    search_fields = ['title', 'description', 'order__order_number', 
                     'order_item__product__name', 'order__user__username']
    readonly_fields = ['order_link', 'order_item_link', 'product_info_display',
                      'image_preview_large', 'uploaded_at_display']
    list_per_page = 20
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_link', 'order_item_link', 'product_info_display')
        }),
        ('Design Details', {
            'fields': ('title', 'description')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at_display', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def id_display(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    id_display.short_description = 'ID'
    id_display.admin_order_field = 'id'
    
    def order_info(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html(
                '<a href="{}">Order #{}</a><br><small>{}</small>',
                url, obj.order.id, obj.order.order_number
            )
        return "—"
    order_info.short_description = 'Order'
    order_info.admin_order_field = 'order__id'
    
    def product_info(self, obj):
        if obj.order_item and obj.order_item.product:
            url = reverse('admin:products_product_change', args=[obj.order_item.product.id])
            return format_html(
                '<a href="{}">{}</a><br><small>Qty: {}</small>',
                url, obj.order_item.product.name, obj.order_item.quantity
            )
        return "—"
    product_info.short_description = 'Product'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 100%;" /><br>'
                '<a href="{}" target="_blank">View Full Image</a>',
                obj.image.url, obj.image.url
            )
        return "No image"
    image_preview_large.short_description = 'Image Preview'
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html(
                '<a href="{}">Order #{}</a> ({})',
                url, obj.order.id, obj.order.order_number
            )
    order_link.short_description = 'Parent Order'
    
    def order_item_link(self, obj):
        if obj.order_item:
            url = reverse('admin:orders_orderitem_change', args=[obj.order_item.id])
            return format_html(
                '<a href="{}">Order Item #{}</a>',
                url, obj.order_item.id
            )
    order_item_link.short_description = 'Order Item'
    
    def product_info_display(self, obj):
        if obj.order_item and obj.order_item.product:
            product = obj.order_item.product
            details = [
                f"<strong>Product:</strong> {product.name}",
                f"<strong>Category:</strong> {product.category.name}",
                f"<strong>Quantity:</strong> {obj.order_item.quantity}",
            ]
            
            if obj.order_item.is_cake:
                details.append(f"<strong>Type:</strong> 🎂 Cake")
                if obj.order_item.cake_flavor:
                    details.append(f"<strong>Flavor:</strong> {obj.order_item.display_flavor}")
                if obj.order_item.cake_weight:
                    details.append(f"<strong>Weight:</strong> {obj.order_item.display_weight}")
            
            return mark_safe('<br>'.join(details))
    product_info_display.short_description = 'Product Details'
    
    def uploaded_at_display(self, obj):
        return obj.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
    uploaded_at_display.short_description = 'Uploaded At'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'order_item', 'order_item__product', 'order_item__product__category'
        ).prefetch_related('order__user')
    
    def has_add_permission(self, request):
        # Design references should be created through order process
        return False