from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_naira')
def format_naira(value):
    """
    Formats a number as Nigerian Naira (NGN) with thousands separators.
    Example: 1234567.89 -> 1,234,567.89
    """
    try:
        if value is None:
            return "₦0.00"
        
        # Convert to Decimal for precise formatting
        val = Decimal(str(value))
        return "₦{:,.2f}".format(val)
    except (ValueError, TypeError):
        return "₦0.00"
