# decorators.py
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

# ==================== USER-TYPE BASED DECORATORS ====================

def customer_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    For customers only (user_type='customer')
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.user_type == 'customer',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    For staff members only (user_type='staff')
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.user_type == 'staff',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def owner_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    For owners/superusers only (user_type='owner')
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.user_type == 'owner',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# ==================== COMBINATION DECORATORS ====================

def staff_or_owner_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    For staff OR owner users
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.user_type in ['staff', 'owner'],
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# ==================== ALIASES FOR BACKWARD COMPATIBILITY ====================

# These aliases match what you're using in admin.py
owner_only = owner_required
staff_or_owner = staff_or_owner_required

# ==================== LEGACY/BACKWARD COMPATIBILITY DECORATORS ====================

def is_staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Checks Django's built-in is_staff field
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def is_superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Checks Django's built-in is_superuser field
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator