# apps/payment/views.py
import hmac
import hashlib
import uuid
import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from orders.models import Order
from cart.models import Cart
from .models import PaymentTransaction
from django.conf import settings


def verify_esewa_signature(data, secret_key):
    """Verify eSewa callback signature"""
    signed_field_names = data.get('signed_field_names', '').split(',')
    
    # Build the string to sign exactly as eSewa expects
    data_to_sign = ""
    for field in signed_field_names:
        if field in data:
            data_to_sign += f"{field}={data[field]},"
    
    if data_to_sign.endswith(','):
        data_to_sign = data_to_sign[:-1]
    
    # Generate expected signature
    key = secret_key.encode('utf-8')
    msg = data_to_sign.encode('utf-8')
    hmac_sha256 = hmac.new(key, msg, hashlib.sha256)
    digest = hmac_sha256.digest()
    expected_signature = base64.b64encode(digest).decode('utf-8')
    
    return expected_signature == data.get('signature', '')


class EsewaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')
        
        if not order_id:
            messages.error(request, 'Order ID is required')
            return redirect('orders:order_list')
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found or you do not have permission')
            return redirect('orders:order_list')
        
        # Check order eligibility
        if order.status != 'pending':
            messages.error(request, 'This order cannot be paid for')
            return redirect('orders:order_detail', order_id=order.id)
        
        if order.payment_method != 'esewa':
            messages.error(request, 'This order is not using eSewa payment')
            return redirect('orders:order_detail', order_id=order.id)
        
        if order.payment_status == 'paid':
            messages.info(request, 'This order has already been paid')
            return redirect('orders:order_confirmation', order_id=order.id)
        
        # Generate unique transaction UUID
        uuid_val = str(uuid.uuid4())

        def genSha256(key, msg):
            key = key.encode('utf-8')
            msg = msg.encode('utf-8')
            hmac_sha256 = hmac.new(key, msg, hashlib.sha256)
            digest = hmac_sha256.digest()
            signature = base64.b64encode(digest).decode('utf-8')
            return signature
        
        secret_key = '8gBm/:&EnhH.1/q'  # TODO: Move to environment variables
        
        # Format the data exactly as eSewa expects
        data_to_sign = f"total_amount={order.total_amount},transaction_uuid={uuid_val},product_code=EPAYTEST"
        signature = genSha256(secret_key, data_to_sign)

        # Create payment transaction record
        payment_transaction = PaymentTransaction.objects.create(
            user=request.user,
            order=order,
            transaction_uuid=uuid_val,
            amount=order.total_amount,
            total_amount=order.total_amount,
            tax_amount=0,
            service_charge=0,
            delivery_charge=0,
            product_code='EPAYTEST',
            signature=signature,
            status='initiated',
        )

        # Build URLs - FIXED: Use kwargs for UUID parameter
        success_url = f"{request.scheme}://{request.get_host}{reverse('orders:order_confirmation', args=[order.id])}?payment=success"
        failure_url = f"{request.scheme}://{request.get_host}{reverse('payment:cancel_payment', kwargs={'transaction_uuid': uuid_val})}"

        data = {
            'amount': str(order.total_amount),
            'total_amount': str(order.total_amount),
            'transaction_uuid': uuid_val,
            'product_code': 'EPAYTEST',
            'signature': signature,
            'success_url': success_url,
            'failure_url': failure_url,
        }

        context = {
            'data': data,
            'order': order,
        }
        
        return render(request, 'payment/esewa_payment.html', context)


@csrf_exempt  # <-- ONLY ONE DECORATOR
def esewa_callback(request):
    """Handle eSewa payment verification callback"""
    if request.method == 'POST':
        try:
            # Get data from eSewa callback
            data = request.POST.dict()
            print(f"eSewa Callback Data: {data}")
            
            # Verify signature
            secret_key = '8gBm/:&EnhH.1/q'
            if not verify_esewa_signature(data, secret_key):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid signature'
                }, status=400)
            
            # Extract required fields
            transaction_uuid = data.get('transaction_uuid')
            status = data.get('status')
            ref_id = data.get('ref_id')
            total_amount = data.get('total_amount')
            
            if not all([transaction_uuid, status]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required parameters'
                }, status=400)
            
            # Find the payment transaction
            try:
                payment = PaymentTransaction.objects.get(transaction_uuid=transaction_uuid)
                
                # Store the callback data
                payment.esewa_status = status
                payment.reference_id = ref_id or ''
                payment.esewa_response_data = data
                
                # Check for CANCELLED/FAILED status explicitly
                if status in ['CANCELLED', 'FAILED', 'ERROR', 'ABORTED']:
                    payment.status = 'failed'
                    payment.save()
                    
                    # Update order status to failed
                    if payment.order:
                        payment.order.payment_status = 'failed'
                        payment.order.status = 'cancelled'
                        payment.order.save()
                    
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'Payment was cancelled or failed'
                    })
                
                # For PENDING status
                elif status == 'PENDING':
                    payment.status = 'pending'
                    payment.save()
                    return JsonResponse({
                        'status': 'pending',
                        'message': 'Payment is pending'
                    })
                
                # For COMPLETE status, verify amount
                elif status == 'COMPLETE':
                    from decimal import Decimal
                    if Decimal(total_amount) != payment.total_amount:
                        payment.status = 'failed'
                        payment.save()
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Amount mismatch'
                        }, status=400)
                    
                    payment.status = 'success'
                    payment.save()
                    
                    # Update the related order
                    if payment.order:
                        order = payment.order
                        order.payment_status = 'paid'
                        order.status = 'confirmed'
                        order.save()
                        
                        # Clear cart if it exists
                        try:
                            Cart.objects.filter(user=order.user).delete()
                        except:
                            pass
                        
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Payment verification completed',
                            'redirect_url': reverse('orders:order_confirmation', kwargs={'order_id': order.id})
                        })
                
                # For any other unknown status
                else:
                    payment.status = 'failed'
                    payment.save()
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Unknown payment status: {status}'
                    })
                    
            except PaymentTransaction.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Transaction not found'
                }, status=404)
                
        except Exception as e:
            print(f"eSewa Callback Error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


def payment_success_redirect(request, transaction_uuid):
    """Redirect to order confirmation after successful payment"""
    try:
        payment = PaymentTransaction.objects.get(transaction_uuid=transaction_uuid)
        if payment.order and payment.status == 'success':
            messages.success(request, 'Payment successful! Your order is now confirmed.')
            return redirect('orders:order_confirmation', order_id=payment.order.id)
        else:
            messages.error(request, 'Payment not found or not successful')
            return redirect('orders:order_list')
    except PaymentTransaction.DoesNotExist:
        messages.error(request, 'Payment transaction not found')
        return redirect('orders:order_list')


def cancel_payment(request, transaction_uuid):
    """Handle payment cancellation from eSewa page"""
    try:
        payment = PaymentTransaction.objects.get(transaction_uuid=transaction_uuid)
        
        # Only allow cancellation if payment is still pending/initiated
        if payment.status in ['pending', 'initiated']:
            payment.status = 'failed'
            payment.esewa_status = 'CANCELLED'
            payment.save()
            
            if payment.order:
                payment.order.payment_status = 'failed'
                payment.order.status = 'cancelled'
                payment.order.save()
                
                messages.warning(request, 'Payment was cancelled. Your order has been cancelled.')
                return redirect('orders:order_detail', order_id=payment.order.id)
        
        messages.info(request, 'This payment cannot be cancelled.')
        return redirect('orders:order_list')
        
    except PaymentTransaction.DoesNotExist:
        messages.error(request, 'Payment transaction not found')
        return redirect('orders:order_list')