# apps/payment/urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('esewa/', views.EsewaView.as_view(), name='esewa'),
    path('esewa/callback/', views.esewa_callback, name='esewa_callback'),
    path('success/<uuid:transaction_uuid>/', views.payment_success_redirect, name='payment_success'),
    path('esewa/cancel/<uuid:transaction_uuid>/', views.cancel_payment, name='cancel_payment'),
]