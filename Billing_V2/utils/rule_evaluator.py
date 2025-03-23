import logging
from .sku_utils import normalize_sku, convert_sku_format

logger = logging.getLogger(__name__)


class RuleEvaluator:
    """
    Class for evaluating business rules against orders.
    """
    
    @staticmethod
    def evaluate_rule(rule, order):
        """
        Evaluate a single rule against an order.
        
        Args:
            rule: Rule object to evaluate
            order: Order object to evaluate against
            
        Returns:
            Boolean indicating if rule applies
        """
        logger.info(f"Evaluating rule: Field={rule.field}, Operator={rule.operator}, Value={(rule.value if hasattr(rule, 'value') else rule.values)}")
        try:
            # Get field value from order
            field = rule.field
            field_value = getattr(order, field, None)
            
            if field_value is None:
                logger.warning(f"Field {field} not found in order {order.transaction_id}")
                return False
                
            # Get rule values
            rule_values = rule.values if hasattr(rule, 'values') else []
            
            # Handle numeric fields
            if field in ['weight_lb', 'line_items', 'total_item_qty']:
                try:
                    field_value = float(field_value or 0)
                    rule_value = float(rule_values[0]) if rule_values else 0
                    
                    # Apply comparison operator
                    operator = rule.operator
                    if operator == 'gt':
                        return field_value > rule_value
                    elif operator == 'lt':
                        return field_value < rule_value
                    elif operator == 'eq':
                        return field_value == rule_value
                    elif operator == 'ne':
                        return field_value != rule_value
                    elif operator == 'ge':
                        return field_value >= rule_value
                    elif operator == 'le':
                        return field_value <= rule_value
                    else:
                        logger.warning(f"Unknown operator {operator} for numeric field {field}")
                        return False
                except (ValueError, IndexError) as e:
                    logger.error(f"Error evaluating numeric rule: {str(e)}")
                    return False
            # Handle string fields
            elif field in ['reference_number', 'ship_to_name', 'ship_to_address', 'ship_to_city', 'notes']:
                field_value = str(field_value or "")
                rule_value = str(rule.value or "") if hasattr(rule, 'value') else ""
                operator = rule.operator
                
                # Make all string comparisons case-insensitive for reference_number and notes
                case_insensitive_fields = ['reference_number', 'notes']
                use_case_insensitive = field in case_insensitive_fields
                
                # Log the field being evaluated
                logger.info(f"Evaluating string field: {field}, Operator: {operator}, Value: '{field_value}', Rule Value: '{rule_value}'")
                
                if operator == 'eq':
                    if use_case_insensitive:
                        if field_value is None:
                            return rule_value is None
                        result = field_value.lower() == rule_value.lower()
                        logger.info(f"Case-insensitive EQ: {field_value.lower()} == {rule_value.lower()} = {result}")
                        return result
                    return field_value == rule_value
                    
                elif operator == 'ne':
                    if use_case_insensitive:
                        if field_value is None:
                            return rule_value is not None
                        result = field_value.lower() != rule_value.lower()
                        logger.info(f"Case-insensitive NE: {field_value.lower()} != {rule_value.lower()} = {result}")
                        return result
                    return field_value != rule_value
                    
                elif operator == 'in':
                    if use_case_insensitive:
                        lower_values = [str(v).lower() for v in rule_values]
                        result = field_value.lower() in lower_values
                        logger.info(f"Case-insensitive IN: {field_value.lower()} in {lower_values} = {result}")
                        return result
                    return field_value in rule_values
                    
                elif operator == 'ni':
                    if use_case_insensitive:
                        lower_values = [str(v).lower() for v in rule_values]
                        result = field_value.lower() not in lower_values
                        logger.info(f"Case-insensitive NOT IN: {field_value.lower()} not in {lower_values} = {result}")
                        return result
                    return field_value not in rule_values
                    
                elif operator == 'contains':
                    if use_case_insensitive:
                        lower_field = field_value.lower()
                        result = any(str(val).lower() in lower_field for val in rule_values)
                        logger.info(f"Case-insensitive CONTAINS = {result}")
                        return result
                    return any(val in field_value for val in rule_values)
                    
                elif operator == 'not_contains':
                    if use_case_insensitive:
                        lower_field = field_value.lower()
                        result = not any(str(val).lower() in lower_field for val in rule_values)
                        logger.info(f"Case-insensitive NOT CONTAINS = {result}")
                        return result
                    return not any(val in field_value for val in rule_values)
                    
                elif operator == 'startswith':
                    if use_case_insensitive:
                        result = field_value.lower().startswith(rule_value.lower())
                        logger.info(f"Case-insensitive STARTSWITH: {field_value.lower()} startswith {rule_value.lower()} = {result}")
                        return result
                    return field_value.startswith(rule_value)
                    
                else:
                    logger.warning(f"Unknown operator {operator} for string field {field}")
                    return False
            
            # Handle SKU quantity fields
            elif field == 'sku_quantity':
                if field_value is None:
                    return False
                    
                # Convert SKU data
                sku_data = convert_sku_format(field_value)
                if not sku_data:
                    return False
                    
                # Extract normalized SKUs for comparison
                normalized_skus = list(sku_data.keys())
                rule_skus = [normalize_sku(sku) for sku in rule_values]
                
                operator = rule.operator
                if operator == 'contains':
                    return any(sku in normalized_skus for sku in rule_skus)
                elif operator == 'not_contains':
                    return not any(sku in normalized_skus for sku in rule_skus)
                elif operator == 'in':
                    return all(sku in rule_skus for sku in normalized_skus)
                elif operator == 'ni':
                    return not all(sku in rule_skus for sku in normalized_skus)
                else:
                    logger.warning(f"Unknown operator {operator} for SKU field")
                    return False
            
            logger.warning(f"Unhandled field {field} or operator {rule.operator}")
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating rule: {str(e)}")
            return False
    
    @staticmethod
    def evaluate_rule_group(rule_group, order):
        """
        Evaluate a rule group against an order.
        
        Args:
            rule_group: RuleGroup object to evaluate
            order: Order object to evaluate against
            
        Returns:
            Boolean indicating if rule group applies
        """
        try:
            # Get all rules for the group
            rules = rule_group.rules.all()
            
            if not rules:
                logger.warning(f"No rules found for rule group {rule_group.id}")
                return False
                
            # Add detailed logging for debugging
            logger.info(f"Evaluating rule group {rule_group.id} with logic '{rule_group.logic_operator}' for order {order.transaction_id}")
            
            # Evaluate each rule with detailed logging
            results = []
            for rule in rules:
                rule_result = RuleEvaluator.evaluate_rule(rule, order)
                results.append(rule_result)
                logger.info(f"Rule result for {rule.field} {rule.operator} '{rule.value if hasattr(rule, 'value') else rule.values}': {rule_result}")
                
                # For reference_number with startswith, add extra debug info
                if rule.field == 'reference_number' and rule.operator == 'startswith':
                    field_value = getattr(order, 'reference_number', None)
                    rule_value = getattr(rule, 'value', None)
                    if field_value and rule_value:
                        logger.info(f"DEBUG - reference_number: '{field_value}', rule value: '{rule_value}', " +
                                   f"lowercase check: '{field_value.lower()}' startswith '{rule_value.lower()}' = {field_value.lower().startswith(rule_value.lower())}")
            
            # Apply logic operator
            logic_operator = rule_group.logic_operator.upper()
            final_result = False
            
            if logic_operator == 'AND':
                final_result = all(results)
                logger.info(f"Rule group {rule_group.id} with AND logic: {results} = {final_result}")
                return final_result
            elif logic_operator == 'OR':
                final_result = any(results)
                logger.info(f"Rule group {rule_group.id} with OR logic: {results} = {final_result}")
                return final_result
            elif logic_operator == 'NOT':
                return not any(results)
            elif logic_operator == 'XOR':
                return results.count(True) == 1
            elif logic_operator == 'NAND':
                return not all(results)
            elif logic_operator == 'NOR':
                return not any(results)
            else:
                logger.warning(f"Unknown logic operator {logic_operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating rule group: {str(e)}")
            return False
    
    @staticmethod
    def evaluate_case_based_rule(rule, order):
        """
        Evaluate a case-based tier rule against an order.
        
        Args:
            rule: AdvancedRule object with tier configuration
            order: Order object to evaluate against
            
        Returns:
            Tuple of (applies, multiplier, case_summary)
        """
        try:
            # Get tier configuration
            tier_config = getattr(rule, 'tier_config', {})
            if not tier_config:
                logger.warning(f"No tier_config found for rule {rule.id}")
                return False, 0, None
                
            # Get excluded SKUs
            excluded_skus = tier_config.get('excluded_skus', [])
            
            # Check if order has get_case_summary method
            if hasattr(order, 'get_case_summary') and callable(getattr(order, 'get_case_summary')):
                case_summary = order.get_case_summary(excluded_skus)
                total_cases = case_summary.get('total_cases', 0)
            else:
                # Fallback to a default summary if the method doesn't exist
                logger.warning(f"Order {order.transaction_id} does not have get_case_summary method")
                case_summary = {'total_cases': 0, 'total_picks': 0, 'sku_breakdown': []}
                total_cases = 0
            
            # If no cases, rule doesn't apply
            if total_cases == 0:
                return False, 0, None
                
            # Check if order has only excluded SKUs - if method exists
            if hasattr(order, 'has_only_excluded_skus') and callable(getattr(order, 'has_only_excluded_skus')):
                if order.has_only_excluded_skus(excluded_skus):
                    return False, 0, None
                
            # Check each tier
            for tier in tier_config.get('ranges', []):
                min_val = tier.get('min', 0)
                max_val = tier.get('max', float('inf'))
                
                if min_val <= total_cases <= max_val:
                    return True, tier.get('multiplier', 0), case_summary
                    
            return False, 0, case_summary
            
        except Exception as e:
            logger.error(f"Error evaluating case-based rule: {str(e)}")
            return False, 0, None