# orders/urls.py 
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cake customization
    path('customize-cake/<int:product_id>/', views.customize_cake, name='customize_cake'),
    
    # Order creation
    path('create/', views.order_create, name='order_create'),
    path('create-with-payment/', views.create_order_with_payment, name='create_order_with_payment'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # Order management
    path('', views.order_list, name='order_list'),
    path('history/', views.order_list, name='order_history'),  
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    
    # Optional routes
    path('track/<str:order_number>/', views.order_track, name='order_track'),
    path('invoice/<int:order_id>/', views.order_invoice_pdf, name='order_invoice_pdf'),
    path('status/<int:order_id>/', views.order_status, name='order_status'),
    
    # Payment handling (add these)
    path('payment-callback/', views.handle_payment_callback, name='payment_callback'),
    path('payment-status/<int:order_id>/', views.payment_status, name='payment_status'),
]