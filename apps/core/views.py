from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import ContactForm
from products.models import Product
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def clear_notification(request):
    """Clear session notification after displaying"""
    if 'notification' in request.session:
        del request.session['notification']
        request.session.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': True})

def home(request):
    featured_products = Product.objects.filter(
        is_featured=True, 
        available=True, 
        in_stock=True    
    )[:4]
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            contact_message = form.save(commit=False)
            
            # Capture additional information
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                contact_message.ip_address = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
            else:
                contact_message.ip_address = request.META.get('REMOTE_ADDR')
            
            contact_message.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            contact_message.save()
            
            # Optional: Send email notification
            try:
                if hasattr(settings, 'ADMIN_EMAIL'):
                    from django.core.mail import send_mail
                    send_mail(
                        subject=f"New Contact Message: {contact_message.get_subject_display()}",
                        message=f"""
New contact message received:

From: {contact_message.full_name}
Email: {contact_message.email}
Phone: {contact_message.phone or 'Not provided'}
Subject: {contact_message.get_subject_display()}

Message:
{contact_message.message}

IP Address: {contact_message.ip_address}
Received: {contact_message.created_at}
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.ADMIN_EMAIL],
                        fail_silently=True,
                    )
            except Exception:
                # Silently fail if email sending doesn't work
                pass
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('core:contact')
        
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

def dashboard_callback(request, context):
    User = get_user_model()  # ✅ CORRECT - Gets your custom user model
    
    from django.db.models import Count
    from django.apps import apps
    
    # Initialize data dictionary
    dashboard_data = {
        'users_count': User.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }
    
    # Safely check for other models
    try:
        Order = apps.get_model('orders', 'Order')
        dashboard_data['orders_count'] = Order.objects.count()
        dashboard_data['pending_orders'] = Order.objects.filter(status='pending').count()
    except (LookupError, AttributeError):
        dashboard_data['orders_count'] = 0
        dashboard_data['pending_orders'] = 0
    
    try:
        Product = apps.get_model('products', 'Product')
        dashboard_data['products_count'] = Product.objects.count()
    except (LookupError, AttributeError):
        dashboard_data['products_count'] = 0
    
    context.update(dashboard_data)
    return context