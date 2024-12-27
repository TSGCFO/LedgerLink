from django import template

register = template.Library()

@register.filter
def format_rule_value(rule):
    """Format rule value based on field type"""
    if rule.field in ['quantity', 'weight', 'volume']:
        return f"{float(rule.value):.2f}"
    return rule.value

@register.filter
def format_adjustment(value):
    """Format adjustment amount with currency symbol"""
    return f"${value:.2f}" if value else "N/A"