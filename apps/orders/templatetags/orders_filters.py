from django import template

register = template.Library()


@register.filter
def get_dict_item(dictionary, key):
    """Get item from dictionary by key in template"""
    return dictionary.get(key, None)

@register.filter(name='filter_by_status')
def filter_by_status(orders, status):
    """Filter orders by status"""
    if not orders:
        return []
    
    if status:
        return [order for order in orders if order.status == status]
    else:
        # Return all except cancelled/completed for "active" filter
        return [order for order in orders if order.status not in ['cancelled', 'completed']]

@register.filter(name='get_form_by_index')
def get_form_by_index(forms_dict, index):
    """Get form by index from dictionary or list."""
    if not forms_dict:
        return None
    
    try:
        index = int(index)
        
        # If forms_dict is a dictionary
        if isinstance(forms_dict, dict):
            keys = list(forms_dict.keys())
            if index < len(keys):
                return forms_dict[keys[index]]
        
        # If forms_dict is a list
        elif isinstance(forms_dict, list):
            if index < len(forms_dict):
                return forms_dict[index]
                
    except (ValueError, TypeError, IndexError):
        pass
    
    return None

# Also register the old name for compatibility
@register.filter(name='filter_status')
def filter_status(orders, status):
    """Alias for filter_by_status"""
    return filter_by_status(orders, status)

@register.filter(name='index')
def index(indexable, i):
    """Get item at index from list or split string"""
    try:
        return indexable[i]
    except (IndexError, TypeError, KeyError):
        return ''
    
# Add to orders_filters.py
@register.filter(name='payment_status_class')
def payment_status_class(payment_status):
    """Return CSS class for payment status badge"""
    if payment_status in ['paid', True]:
        return 'bg-green-100 text-green-800'
    elif payment_status in ['failed', 'cancelled']:
        return 'bg-red-100 text-red-800'
    elif payment_status in ['pending', False]:
        return 'bg-yellow-100 text-yellow-800'
    else:
        return 'bg-gray-100 text-gray-800'

@register.filter(name='payment_status_display')
def payment_status_display(payment_status):
    """Return display text for payment status"""
    if payment_status in ['paid', True]:
        return 'Paid'
    elif payment_status in ['failed', 'cancelled']:
        return 'Failed'
    elif payment_status in ['pending', False]:
        return 'Pending'
    else:
        return str(payment_status).title() if payment_status else 'Pending'