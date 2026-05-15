from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def expiry_time(value):
    # Adds 6 hours to the creation time
    return value + timedelta(hours=6)