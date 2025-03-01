"""
Test script for the RuleEngine case-based tier evaluation.
This simulates the frontend rule evaluation logic without requiring a React environment.
"""

import sys
import json
from pathlib import Path
import os

# Mock the RuleEngine.js logic to test case-based tier evaluation
class RuleEngine:
    def evaluateCaseBasedTier(self, rule, context):
        try:
            tier_config = rule.get('tier_config', {})
            if not tier_config or not tier_config.get('ranges'):
                return {'success': False, 'reason': 'Missing tier configuration'}

            # Get total cases excluding specified SKUs
            totalCases = self.calculateTotalCases(context, tier_config.get('excluded_skus', []))
            
            # Find applicable tier
            applicableTier = None
            for tier in tier_config.get('ranges', []):
                if totalCases >= tier['min'] and totalCases <= tier['max']:
                    applicableTier = tier
                    break

            if applicableTier:
                return {
                    'success': True,
                    'reason': f"Matches tier: {totalCases} cases falls between {applicableTier['min']} and {applicableTier['max']}",
                    'multiplier': applicableTier['multiplier']
                }

            return {
                'success': False,
                'reason': f"No matching tier for {totalCases} cases"
            }
        except Exception as e:
            return {
                'success': False,
                'reason': f"Case-based tier evaluation error: {str(e)}"
            }

    def calculateTotalCases(self, context, excludedSkus=[]):
        try:
            sku_quantity = context.get('sku_quantity', {})
            if not sku_quantity:
                return 0

            totalCases = 0
            normalizedExcluded = set([sku.upper().strip() for sku in excludedSkus])

            for sku, data in sku_quantity.items():
                if sku.upper().strip() not in normalizedExcluded:
                    totalCases += data.get('cases', 0)

            return totalCases
        except Exception as e:
            print(f"Error calculating total cases: {e}")
            return 0

    def calculateAdjustments(self, rule, baseAmount, context):
        if rule.get('calculations', []):
            for calc in rule.get('calculations', []):
                if calc.get('type') == 'case_based_tier':
                    evaluation = self.evaluateCaseBasedTier(rule, context)
                    if evaluation.get('success'):
                        return baseAmount * evaluation.get('multiplier', 1.0)
            
        # Default to base amount if no adjustments apply
        return baseAmount


def run_tests():
    """Run tests for RuleEngine case-based tier evaluation"""
    print("Running RuleEngine Case-Based Tier Tests")
    print("-" * 50)
    
    engine = RuleEngine()
    
    # Test case 1: Valid rule with excluded SKU
    order1 = {
        'sku_quantity': {
            'SKU1': {'quantity': 5, 'cases': 2},
            'SKU2': {'quantity': 10, 'cases': 3},
            'SKU3': {'quantity': 5, 'cases': 1}
        }
    }
    
    rule1 = {
        'field': 'sku_quantity',
        'operator': 'contains',
        'value': 'SKU1',
        'calculations': [
            {'type': 'case_based_tier', 'value': 1.0}
        ],
        'tier_config': {
            'ranges': [
                {'min': 1, 'max': 3, 'multiplier': 1.0},
                {'min': 4, 'max': 6, 'multiplier': 2.0},
                {'min': 7, 'max': 10, 'multiplier': 3.0}
            ],
            'excluded_skus': ['SKU3']
        }
    }
    
    # Expected: SKU1(2) + SKU2(3) = 5 cases, excludes SKU3(1)
    # Should match the second tier (4-6 cases) with multiplier 2.0
    
    print("\nTest 1: Rule with excluded SKU")
    base_amount = 100.0
    result = engine.calculateAdjustments(rule1, base_amount, order1)
    expected = base_amount * 2.0  # Second tier multiplier
    
    if result == expected:
        print(f"✅ Calculation correct: {result} (Expected: {expected})")
    else:
        print(f"❌ Calculation incorrect: {result} (Expected: {expected})")
    
    # Test case 2: Total matches the highest tier
    order2 = {
        'sku_quantity': {
            'SKU1': {'quantity': 5, 'cases': 5},
            'SKU2': {'quantity': 10, 'cases': 10},
        }
    }
    
    rule2 = {
        'field': 'sku_quantity',
        'operator': 'contains',
        'value': 'SKU1',
        'calculations': [
            {'type': 'case_based_tier', 'value': 1.0}
        ],
        'tier_config': {
            'ranges': [
                {'min': 1, 'max': 3, 'multiplier': 1.0},
                {'min': 4, 'max': 10, 'multiplier': 2.0},
                {'min': 11, 'max': 15, 'multiplier': 3.0}
            ],
            'excluded_skus': []
        }
    }
    
    print("\nTest 2: Case total matches the highest tier")
    base_amount = 100.0
    result = engine.calculateAdjustments(rule2, base_amount, order2)
    expected = base_amount * 3.0  # Third tier multiplier for 15 total cases
    
    if result == expected:
        print(f"✅ Calculation correct: {result} (Expected: {expected})")
    else:
        print(f"❌ Calculation incorrect: {result} (Expected: {expected})")
    
    # Test case 3: No matching tier
    order3 = {
        'sku_quantity': {
            'SKU1': {'quantity': 5, 'cases': 20},
            'SKU2': {'quantity': 10, 'cases': 5},
        }
    }
    
    print("\nTest 3: No matching tier (outside range)")
    base_amount = 100.0
    result = engine.calculateAdjustments(rule2, base_amount, order3)
    expected = base_amount  # No matching tier, so no adjustment
    
    if result == expected:
        print(f"✅ Calculation correct: {result} (Expected: {expected})")
    else:
        print(f"❌ Calculation incorrect: {result} (Expected: {expected})")
    
    print("\n" + "-" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    run_tests()