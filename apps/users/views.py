from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import CustomerCreationForm, CustomAuthenticationForm
from .decoraters import customer_required, staff_required, owner_required, staff_or_owner_required

def register(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'owner':
            messages.info(request, "You are already logged in as owner.")
            return redirect('admin:index')
        elif request.user.user_type == 'staff':
            messages.info(request, "You are already logged in as staff.")
            return redirect('admin:index')
        else:
            messages.info(request, "You are already logged in.")
            return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Live Bakery!")
            return redirect('core:home')
    else:
        form = CustomerCreationForm()
    return render(request, 'users/register.html', {'form': form})

def custom_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'owner' or request.user.is_superuser:
            messages.info(request, "You are already logged in as owner/superuser.")
            return redirect('admin:index')
        elif request.user.user_type == 'staff':
            messages.info(request, "You are already logged in as staff.")
            return redirect('admin:index')
        else:
            messages.info(request, "You are already logged in.")
            return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Check user type and redirect accordingly
                if user.user_type == 'owner' or user.is_superuser:
                    messages.info(request, f"Welcome back, Owner/Superuser {user.username}!")
                    return redirect('admin:index')
                elif user.user_type == 'staff':
                    messages.info(request, f"Welcome back, Staff {user.username}!")
                    return redirect('admin:index')
                else:
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('core:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
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