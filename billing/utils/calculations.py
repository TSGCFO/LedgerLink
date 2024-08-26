# billing/utils/calculations.py

from decimal import Decimal

def apply_discount(amount, discount):
    """Apply a percentage discount to a given amount."""
    discount_amount = (amount * Decimal(discount) / 100).quantize(Decimal('0.01'))
    return amount - discount_amount

def calculate_tax(amount, tax_rate):
    """Calculate the tax for a given amount based on a tax rate."""
    tax_amount = (amount * Decimal(tax_rate) / 100).quantize(Decimal('0.01'))
    return tax_amount

def calculate_total_with_tax(amount, tax_rate):
    """Calculate the total amount including tax."""
    tax_amount = calculate_tax(amount, tax_rate)
    return amount + tax_amount
