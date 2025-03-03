#!/usr/bin/env python
"""Debug the contains/ncontains logic."""

# Test simple string operations
field_value = "UNITED STATES"
test_value = "US"

print(f"Lower case test:")
print(f"field_value.lower(): {field_value.lower()}")
print(f"test_value.lower(): {test_value.lower()}")
print(f"test_value.lower() in field_value.lower(): {test_value.lower() in field_value.lower()}")

# Test with different country values
countries = ["United States", "UNITED STATES", "united states", "USA", "U.S.A.", "Canada"]
print("\nTesting 'US' substring in different countries:")
for country in countries:
    result = test_value.lower() in country.lower()
    print(f"'{test_value}' in '{country}': {result}")