from decimal import Decimal


def apply_discount(amount, discount):
    """
    Apply a percentage discount to a given amount.

    :param amount: The original amount before the discount.
    :type amount: Decimal
    :param discount: The discount percentage to be applied.
    :type discount: float
    :return: The final amount after applying the discount.
    :rtype: Decimal
    """
    discount_amount = (amount * Decimal(discount) / 100).quantize(Decimal("0.01"))
    return amount - discount_amount


def calculate_tax(amount, tax_rate):
    """
    Calculate the tax for a given amount based on a tax rate.

    :param amount: The total amount of money on which tax needs to be calculated.
    :type amount: Decimal
    :param tax_rate: The percentage rate at which the tax is to be calculated.
    :type tax_rate: float
    :return: The calculated tax amount, rounded to 2 decimal places.
    :rtype: Decimal
    """
    tax_amount = (amount * Decimal(tax_rate) / 100).quantize(Decimal("0.01"))
    return tax_amount


def calculate_total_with_tax(amount, tax_rate):
    """
    Calculate the total amount including tax.

    :param amount: The initial monetary amount before the tax is applied.
    :type amount: Decimal
    :param tax_rate: The tax rate to be applied to the amount.
    :type tax_rate: float
    :return: The total amount including tax.
    :rtype: Decimal
    """
    tax_amount = calculate_tax(amount, tax_rate)
    return amount + tax_amount
