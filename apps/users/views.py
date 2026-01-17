from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomerCreationForm, CustomAuthenticationForm
from .decoraters import customer_required, staff_required, owner_required, staff_or_owner_required

def custom_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'owner' or request.user.is_superuser:
            return redirect('admin:index')
        elif request.user.user_type == 'staff':
            return redirect('admin:index')
        else:
            return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                first_name = user.first_name if user.first_name else user.username
                
                # Set notification in session
                if user.user_type == 'owner' or user.is_superuser:
                    request.session['notification'] = {
                        'type': 'info',
                        'message': f'Welcome back, {first_name}! (Owner)'
                    }
                    return redirect('admin:index')
                elif user.user_type == 'staff':
                    request.session['notification'] = {
                        'type': 'info',
                        'message': f'Welcome back, {first_name}! (Staff)'
                    }
                    return redirect('admin:index')
                else:
                    request.session['notification'] = {
                        'type': 'success',
                        'message': f'Welcome back, {first_name}! 🎉'
                    }
                    request.session.save()  # Ensure session is saved
                    return redirect('core:home')
        
        # Login failed
        error_message = 'Invalid username or password.'
        return render(request, 'users/login.html', {
            'form': form,
            'error_notification': {
                'type': 'error',
                'message': error_message
            }
        })
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'owner':
            return redirect('admin:index')
        elif request.user.user_type == 'staff':
            return redirect('admin:index')
        else:
            return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            first_name = user.first_name if user.first_name else user.username
            
            # Store notification data in session
            request.session['notification'] = {
                'type': 'success',
                'message': f'Account created successfully! Welcome to Live Bakery, {first_name}! 🍰'
            }
            request.session.save()  # Ensure session is saved
            
            return redirect('core:home')
    else:
        form = CustomerCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

def custom_logout(request):
    user_first_name = request.user.first_name or request.user.username
    logout(request)
    
    # Store notification in session for display on redirect
    request.session['notification'] = {
        'type': 'success',
        'message': f'You have been successfully logged out. Goodbye, {user_first_name}! 👋'
    }
    request.session.save()  # Ensure session is saved
    
    return redirect('core:home')

@login_required
@customer_required
def profile(request):
    context = {
        'user': request.user,
        'is_customer': True
    }
    return render(request, 'users/profile.html', context)

@login_required
@customer_required
def user_orders(request):
    from orders.models import Order
    orders_list = Order.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1
    }
    return render(request, 'users/orders.html', context)