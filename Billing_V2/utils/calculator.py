import logging
import json
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from customers.models import Customer
from orders.models import Order
from products.models import Product
from customer_services.models import CustomerService
from rules.models import RuleGroup
from .sku_utils import normalize_sku, convert_sku_format
from .rule_evaluator import RuleEvaluator
from decimal import getcontext
# Set precision for decimal calculations
getcontext().prec = 28
from ..models import BillingReport, OrderCost, ServiceCost

logger = logging.getLogger(__name__)


class BillingCalculator:
    """
    Class for calculating billing reports.
    """
    
    def __init__(self, customer_id, start_date, end_date, customer_service_ids=None):
        """
        Initialize the calculator with customer and date range.
        
        Args:
            customer_id: ID of the customer
            start_date: Start date for billing period
            end_date: End date for billing period
            customer_service_ids: Optional list of customer service IDs to include
                                 (if None or empty, all services are included)
        """
        self.customer_id = customer_id
        self.customer_service_ids = customer_service_ids
        self.progress = {
            'status': 'initializing',
            'percent_complete': 0,
            'current_step': 'Initializing calculator',
            'total_orders': 0,
            'processed_orders': 0,
            'start_time': timezone.now(),
            'estimated_completion_time': None
        }
        
        # Convert dates to timezone-aware datetimes if needed
        if isinstance(start_date, datetime) and start_date.tzinfo is None:
            self.start_date = timezone.make_aware(start_date)
        elif not isinstance(start_date, datetime):
            # Convert date to datetime at midnight
            self.start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
        else:
            self.start_date = start_date
            
        if isinstance(end_date, datetime) and end_date.tzinfo is None:
            self.end_date = timezone.make_aware(end_date)
        elif not isinstance(end_date, datetime):
            # Convert date to datetime at 23:59:59
            self.end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
        else:
            self.end_date = end_date
        
        # Create empty report
        self.report = BillingReport(
            customer_id=customer_id,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=0,
            service_totals={}
        )
        
        # Store metadata about customer service selection in report metadata
        self.report.metadata = {
            'selected_services': customer_service_ids
        }
        
    def update_progress(self, status, current_step, percent_complete=None):
        """
        Update the progress tracking information.
        
        Args:
            status: Current status (initializing, processing, completed, error)
            current_step: Description of the current step
            percent_complete: Optional percent complete (0-100)
        """
        self.progress['status'] = status
        self.progress['current_step'] = current_step
        
        if percent_complete is not None:
            self.progress['percent_complete'] = percent_complete
            
        # Calculate estimated completion time
        if self.progress['percent_complete'] > 0:
            elapsed_time = (timezone.now() - self.progress['start_time']).total_seconds()
            estimated_total_time = elapsed_time / (self.progress['percent_complete'] / 100)
            estimated_remaining = estimated_total_time - elapsed_time
            
            if estimated_remaining > 0:
                estimated_completion = timezone.now() + timezone.timedelta(seconds=estimated_remaining)
                self.progress['estimated_completion_time'] = estimated_completion
                
        # Add current timestamp to progress
        self.progress['updated_at'] = timezone.now().isoformat()
        
        # Log progress updates 
        logger.info(f"Progress: {self.progress['percent_complete']}% - {self.progress['current_step']}")
        
        # Update progress in cache if we have customer_id and dates
        if hasattr(self, 'customer_id') and hasattr(self, 'start_date') and hasattr(self, 'end_date'):
            try:
                from django.core.cache import cache
                progress_key = f"billing_report_progress_{self.customer_id}_{self.start_date.strftime('%Y-%m-%d')}_{self.end_date.strftime('%Y-%m-%d')}"
                cache.set(progress_key, self.progress, 3600)  # Cache for 1 hour
            except Exception as e:
                logger.error(f"Error updating progress in cache: {str(e)}")
    
    def validate_input(self):
        """
        Validate the input parameters.
        
        Raises:
            ValidationError: If input is invalid
        """
        try:
            # Check customer exists
            customer = Customer.objects.filter(id=self.customer_id).first()
            if not customer:
                raise ValidationError(f"Customer with ID {self.customer_id} not found")
                
            # Check date range
            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before end date")
                
            # Check customer has services
            if not CustomerService.objects.filter(customer_id=self.customer_id).exists():
                raise ValidationError(f"No services found for customer {self.customer_id}")
                
        except Exception as e:
            logger.error(f"Error validating input: {str(e)}")
            raise
    
    @transaction.atomic
    def generate_report(self):
        """
        Generate billing report for customer and date range.
        
        Returns:
            BillingReport object
        """
        try:
            # Update progress
            self.update_progress('initializing', 'Validating input', 5)
            
            # Validate input
            self.validate_input()
            
            # Start timing
            import time
            start_time = time.time()
            
            # Save the report
            self.report.save()
            
            # Update progress
            self.update_progress('processing', 'Finding orders for date range', 10)
            
            logger.info(f"Generating billing report for customer {self.customer_id} from {self.start_date} to {self.end_date}")
            
            # Get all orders for customer in date range
            # Use select_related to fetch customer data in a single query
            orders = Order.objects.filter(
                customer_id=self.customer_id,
                close_date__gte=self.start_date,
                close_date__lte=self.end_date
            ).select_related('customer').order_by('close_date')
            
            # Convert queryset to list to avoid repeated database hits
            orders_list = list(orders)
            order_count = len(orders_list)
            logger.info(f"Found {order_count} orders for billing period")
            
            # Update progress tracking
            self.progress['total_orders'] = order_count
            
            if not orders_list:
                logger.info(f"No orders found for customer {self.customer_id} in date range")
                self.update_progress('completed', 'No orders found', 100)
                return self.report
            
            # Update progress
            self.update_progress('processing', 'Loading customer services', 15)
            
            # Get filtered customer services if specified
            customer_services_query = CustomerService.objects.filter(
                customer_id=self.customer_id
            )
            
            # Apply service filter if specified
            if self.customer_service_ids is not None:
                customer_services_query = customer_services_query.filter(
                    id__in=self.customer_service_ids
                )
                
            # Get all customer services with related data
            customer_services = list(customer_services_query.select_related('service'))
            
            # Check if we have any services to process
            if not customer_services:
                logger.warning(f"No valid customer services found for report")
                self.update_progress('completed', 'No valid customer services found', 100)
                return self.report
                
            # Update progress
            self.update_progress('processing', 'Loading business rules', 20)
            
            # Get rule groups for each customer service in a single query
            from django.db.models import Prefetch
            rule_groups = RuleGroup.objects.filter(
                customer_service__in=[cs.id for cs in customer_services]
            ).select_related('customer_service')
            
            # Group rule groups by customer service
            rule_groups_by_service = {}
            for rule_group in rule_groups:
                cs_id = rule_group.customer_service_id
                if cs_id not in rule_groups_by_service:
                    rule_groups_by_service[cs_id] = []
                rule_groups_by_service[cs_id].append(rule_group)
            
            # Prepare for bulk operations
            order_costs_to_create = []
            service_costs_to_create = []
            order_costs_to_delete = []
            
            # Cache for rule evaluations to avoid redundant computations
            rule_evaluation_cache = {}
            
            # Process orders in batches to optimize memory usage
            batch_size = 100
            total_batches = (order_count + batch_size - 1) // batch_size
            
            # Initial progress after setup
            progress_per_batch = 70 / total_batches  # 70% of progress is in batch processing
            
            for batch_index in range(total_batches):
                start_idx = batch_index * batch_size
                end_idx = min((batch_index + 1) * batch_size, order_count)
                batch_orders = orders_list[start_idx:end_idx]
                
                # Update progress
                progress = 20 + ((batch_index / total_batches) * 70)
                batch_desc = f"Processing orders {start_idx+1}-{end_idx} of {order_count}"
                self.update_progress('processing', batch_desc, progress)
                
                logger.info(f"Processing batch {batch_index + 1}/{total_batches} ({len(batch_orders)} orders)")
                
                # Create order costs for this batch
                batch_order_costs = []
                for order in batch_orders:
                    order_cost = OrderCost(
                        order=order,
                        billing_report=self.report
                    )
                    batch_order_costs.append(order_cost)
                
                # Bulk create order costs
                created_order_costs = OrderCost.objects.bulk_create(batch_order_costs)
                
                # Process each order with its order cost
                for i, order in enumerate(batch_orders):
                    order_cost = created_order_costs[i]
                    
                    # Track applied single services
                    applied_single_services = set()
                    batch_service_costs = []
                    
                    # Process each customer service
                    for cs in customer_services:
                        # Skip if single service already applied
                        if cs.service.charge_type == 'single' and cs.service.id in applied_single_services:
                            continue
                            
                        # Get rule groups for this service
                        rule_groups = rule_groups_by_service.get(cs.id, [])
                        
                        # If no rule groups, service applies
                        service_applies = len(rule_groups) == 0
                        
                        # Otherwise, check if any rule group applies
                        if not service_applies:
                            # Check cache first to avoid redundant evaluations
                            # Use transaction_id which is guaranteed to exist instead of id
                            cache_key = (order.transaction_id, cs.id)
                            if cache_key in rule_evaluation_cache:
                                service_applies = rule_evaluation_cache[cache_key]
                            else:
                                for rule_group in rule_groups:
                                    if rule_group.evaluate(order):
                                        service_applies = True
                                        break
                                # Cache result
                                rule_evaluation_cache[cache_key] = service_applies
                                
                        # If service applies, calculate and add cost
                        if service_applies:
                            amount = self.calculate_service_cost(cs, order)
                            
                            # Only create cost if amount > 0
                            if amount > 0:
                                service_cost = ServiceCost(
                                    order_cost=order_cost,
                                    service_id=cs.service.id,
                                    service_name=cs.service.service_name,
                                    amount=amount
                                )
                                batch_service_costs.append(service_cost)
                                
                                # Update report totals
                                service_id = str(cs.service.id)
                                if service_id in self.report.service_totals:
                                    self.report.service_totals[service_id]['amount'] += float(amount)
                                else:
                                    self.report.service_totals[service_id] = {
                                        'service_name': cs.service.service_name,
                                        'amount': float(amount)
                                    }
                                
                                # Don't update total_amount here - will be handled by update_total_amount
                                    
                                # Track applied single services
                                if cs.service.charge_type == 'single':
                                    applied_single_services.add(cs.service.id)
                    
                    # Add service costs to the batch
                    if batch_service_costs:
                        service_costs_to_create.extend(batch_service_costs)
                        # Update order total - will be saved at the end
                        total_amount = sum(sc.amount for sc in batch_service_costs)
                        order_cost.total_amount = total_amount
                        # Update service totals without updating total_amount (already updated per service cost)
                        self.report.add_order_cost(order_cost)
                    else:
                        # Mark for deletion if no service costs
                        order_costs_to_delete.append(order_cost)
                    
                    # Update processed order count
                    self.progress['processed_orders'] += 1
                
                # Update progress within batch
                sub_progress = 20 + ((batch_index + 0.5) / total_batches * 70)
                self.update_progress(
                    'processing', 
                    f"Creating service records for batch {batch_index + 1}/{total_batches}",
                    sub_progress
                )
                
                # Bulk create service costs for this batch
                if service_costs_to_create:
                    # Create in smaller chunks to avoid memory issues
                    max_chunk_size = 1000
                    for j in range(0, len(service_costs_to_create), max_chunk_size):
                        chunk = service_costs_to_create[j:j+max_chunk_size]
                        ServiceCost.objects.bulk_create(chunk)
                    service_costs_to_create = []
                
                # Free up memory
                del batch_orders
                del batch_order_costs
                del created_order_costs
            
            # Update progress
            self.update_progress('processing', 'Cleaning up temporary records', 90)
            
            # Delete empty order costs
            if order_costs_to_delete:
                # Use pk which always exists instead of id
                order_ids_to_delete = [oc.pk for oc in order_costs_to_delete]
                OrderCost.objects.filter(pk__in=order_ids_to_delete).delete()
                logger.info(f"Deleted {len(order_ids_to_delete)} empty order costs")
            
            # Update progress
            self.update_progress('processing', 'Saving final report', 95)
            
            # Always recalculate and update the total amount at the end to ensure accuracy
            # This addresses issues where reports with filtered services might not show correct totals
            if self.report.service_totals:
                total = sum(data['amount'] for data in self.report.service_totals.values())
                if abs(float(self.report.total_amount) - total) > 0.01:  # Allow for small decimal differences
                    self.report.total_amount = total
                    logger.info(f"Final report generation: Updated total amount to {total} based on service totals")
            else:
                # No services - total should be zero
                self.report.total_amount = 0
                logger.info("Final report generation: Set total amount to zero (no service totals)")
            
            # Save the report with final totals using an explicit transaction
            from django.db import transaction
            with transaction.atomic():
                self.report.save()
            
            # Log performance metrics
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Report generation completed in {execution_time:.2f} seconds with total amount {self.report.total_amount}")
            
            # Update final progress
            self.update_progress('completed', 'Report generation complete', 100)
            
            return self.report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            # Update progress to error state
            self.update_progress('error', f"Error: {str(e)}", None)
            # Re-raise as proper error
            if isinstance(e, ValidationError):
                raise
            else:
                raise ValidationError(f"Error generating report: {str(e)}")
    
    # Keep a cache of precomputed SKU lists and product maps at the class level
    _excluded_skus_cache = {}
    _product_map_cache = {}
    
    def calculate_service_cost(self, customer_service, order):
        """
        Calculate the cost for a service applied to an order.
        
        Args:
            customer_service: CustomerService object
            order: Order object
            
        Returns:
            Decimal cost amount
        """
        try:
            service = customer_service.service
            charge_type = service.charge_type.lower()
            
            # Handle case-based tier pricing
            if charge_type == 'case_based_tier':
                try:
                    # Access cached advanced rules if available
                    cache_key = f"adv_rules_{customer_service.id}"
                    if hasattr(self, cache_key):
                        advanced_rules = getattr(self, cache_key)
                    else:
                        # Get advanced rules associated with this customer service via rule groups
                        from rules.models import AdvancedRule, RuleGroup
                        
                        # Find rule groups for this customer service with a more efficient query
                        advanced_rules = list(AdvancedRule.objects.filter(
                            rule_group__customer_service=customer_service
                        ).select_related('rule_group'))
                        
                        # Cache for future use
                        setattr(self, cache_key, advanced_rules)
                    
                    if not advanced_rules:
                        logger.warning(f"No advanced rules found for customer service {customer_service.id}")
                        return Decimal('0')
                    
                    # Use the first one found for now
                    advanced_rule = advanced_rules[0]
                    
                    # For now, we'll return a simple calculation
                    # This is marked for future implementation
                    logger.debug("Case-based tier calculation not fully implemented")
                    return customer_service.unit_price or Decimal('0')
                    
                except Exception as e:
                    logger.error(f"Error evaluating case-based rule: {str(e)}")
                    return Decimal('0')
            
            # If no unit price, return 0
            if not customer_service.unit_price:
                return Decimal('0')
                
            # Set base price
            base_price = customer_service.unit_price
            
            # Convert service name to lowercase for comparison - do this once and cache
            if not hasattr(customer_service, '_service_name_lower'):
                customer_service._service_name_lower = service.service_name.lower()
            service_name = customer_service._service_name_lower
            
            # Handle quantity-based services
            if charge_type == 'quantity':
                # If service has assigned SKUs - get them from the M2M relationship
                if not hasattr(customer_service, '_assigned_skus'):
                    assigned_skus_list = customer_service.get_sku_list()
                    customer_service._assigned_skus = [normalize_sku(sku) for sku in assigned_skus_list] if assigned_skus_list else []
                
                assigned_skus = customer_service._assigned_skus
                
                if assigned_skus:
                    # Get SKU quantities from order
                    sku_quantity = getattr(order, 'sku_quantity', None)
                    if not sku_quantity:
                        return Decimal('0')
                    
                    # Convert order SKUs to normalized format - cache if not already done
                    if not hasattr(order, '_normalized_sku_dict'):
                        order._normalized_sku_dict = convert_sku_format(sku_quantity)
                    sku_dict = order._normalized_sku_dict
                    
                    # Create a set from assigned_skus for faster lookup
                    if not hasattr(customer_service, '_assigned_skus_set'):
                        customer_service._assigned_skus_set = set(assigned_skus)
                    assigned_skus_set = customer_service._assigned_skus_set
                    
                    # Calculate total quantity for matching SKUs
                    total_quantity = sum(
                        quantity for sku, quantity in sku_dict.items() 
                        if sku in assigned_skus_set
                    )
                    
                    if total_quantity == 0:
                        return Decimal('0')
                        
                    return base_price * Decimal(str(total_quantity))
                
                # Special handling for pick cost and case pick
                if service_name in ['pick cost', 'case pick']:
                    # Get SKU quantities from order
                    sku_quantity = getattr(order, 'sku_quantity', None)
                    if not sku_quantity:
                        return Decimal('0')
                    
                    # Convert order SKUs to normalized format - use cached if available
                    if not hasattr(order, '_normalized_sku_dict'):
                        order._normalized_sku_dict = convert_sku_format(sku_quantity)
                    sku_dict = order._normalized_sku_dict
                    
                    # Get excluded SKUs - use cached version if available
                    customer_id = order.customer_id
                    if customer_id not in self._excluded_skus_cache:
                        # Query once and cache the results
                        excluded_skus = []
                        quantity_services = CustomerService.objects.filter(
                            customer_id=customer_id,
                            service__charge_type='quantity'
                        ).select_related('service')
                        
                        for cs in quantity_services:
                            skus_list = cs.get_sku_list()
                            if skus_list:
                                excluded_skus.extend([normalize_sku(sku) for sku in skus_list])
                        
                        self._excluded_skus_cache[customer_id] = set(excluded_skus)
                    
                    excluded_skus_set = self._excluded_skus_cache[customer_id]
                    
                    # Filter out excluded SKUs - use dict comprehension for efficiency
                    applicable_skus = {
                        sku: qty for sku, qty in sku_dict.items() 
                        if sku not in excluded_skus_set
                    }
                    
                    if not applicable_skus:
                        return Decimal('0')
                    
                    # Get products for these SKUs - use cached version if available
                    skus_list = list(applicable_skus.keys())
                    # Create a stable string representation for the cache key
                    skus_key = ",".join(sorted(skus_list))
                    if skus_key not in self._product_map_cache:
                        # Get all products in one query
                        products = Product.objects.filter(sku__in=skus_list)
                        
                        # Build product map
                        product_map = {}
                        for product in products:
                            normalized_sku = normalize_sku(product.sku)
                            product_map[normalized_sku] = product
                        
                        self._product_map_cache[skus_key] = product_map
                    
                    product_map = self._product_map_cache[skus_key]
                    
                    # Initialize total cost
                    total_cost = Decimal('0')
                    
                    # Calculate cost for each SKU
                    for sku, quantity in applicable_skus.items():
                        product = product_map.get(sku)
                        if not product:
                            continue
                        
                        # Get case_size safely, falling back to 1 if not available
                        case_size = 1
                        if hasattr(product, 'case_size'):
                            case_size = product.case_size or 1
                        
                        if service_name == 'case pick':
                            # Case pick: only charge for full cases
                            full_cases = quantity // case_size
                            if full_cases > 0:
                                total_cost += base_price * Decimal(str(full_cases))
                        else:  # pick cost
                            # Pick cost: charge for remaining units or all units
                            units = quantity % case_size if case_size > 1 else quantity
                            if units > 0:
                                total_cost += base_price * Decimal(str(units))
                    
                    return total_cost
                
                # Handle SKU cost (charging per unique SKU)
                elif service_name == 'sku cost':
                    sku_quantity = getattr(order, 'sku_quantity', None)
                    if not sku_quantity:
                        return Decimal('0')
                    
                    # Use cached conversion if available
                    if not hasattr(order, '_normalized_sku_dict'):
                        order._normalized_sku_dict = convert_sku_format(sku_quantity)
                    
                    unique_sku_count = len(order._normalized_sku_dict)
                    return base_price * Decimal(str(unique_sku_count))
                
                # Regular quantity-based service
                else:
                    quantity = getattr(order, 'total_item_qty', 1) or 1
                    return base_price * Decimal(str(quantity))
            
            # Handle single charge
            elif charge_type == 'single':
                return base_price
            
            logger.debug(f"Unknown charge type: {charge_type}")
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Error calculating service cost: {str(e)}")
            return Decimal('0')
    
    def to_dict(self):
        """
        Convert report to dictionary format.
        
        Returns:
            Dictionary representation of report
        """
        try:
            return self.report.to_dict()
        except Exception as e:
            logger.error(f"Error converting report to dict: {str(e)}")
            raise
    
    def to_json(self):
        """
        Convert report to JSON format.
        
        Returns:
            JSON string representation of report
        """
        try:
            return self.report.to_json()
        except Exception as e:
            logger.error(f"Error converting report to JSON: {str(e)}")
            raise
    
    def to_csv(self):
        """
        Convert report to CSV format.
        
        Returns:
            CSV string representation of report
        """
        try:
            # Create header line
            lines = ["order_id,reference_number,date,service_id,service_name,amount"]
            
            # Process each order and its service costs
            for order_cost in self.report.order_costs.all():
                order = order_cost.order
                reference = order.reference_number.replace('"', '""') if order.reference_number else ""
                date = order.close_date.strftime('%Y-%m-%d') if order.close_date else ""
                
                for service_cost in order_cost.service_costs.all():
                    # Format service name for CSV (escape quotes)
                    service_name = service_cost.service_name.replace('"', '""') if service_cost.service_name else ""
                    
                    # Build CSV line
                    line = f"{order.transaction_id},\"{reference}\",{date},{service_cost.service_id},"
                    line += f"\"{service_name}\",{service_cost.amount}"
                    lines.append(line)
            
            # Add a summary section
            lines.append("")
            lines.append("SUMMARY")
            lines.append("service_id,service_name,total_amount")
            
            for service_id, data in self.report.service_totals.items():
                service_name = data['service_name'].replace('"', '""') if data['service_name'] else ""
                lines.append(f"{service_id},\"{service_name}\",{data['amount']}")
            
            lines.append("")
            lines.append(f"TOTAL,\"\",{self.report.total_amount}")
                    
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error converting report to CSV: {str(e)}")
            raise


def generate_billing_report(customer_id, start_date, end_date, output_format='json'):
    """
    Entry point for generating billing reports.
    
    Args:
        customer_id: ID of the customer
        start_date: Start date for billing period (string or datetime)
        end_date: End date for billing period (string or datetime)
        output_format: Format for output (json, csv, dict)
        
    Returns:
        Report data in the specified format
        
    Raises:
        ValidationError: If input is invalid
    """
    try:
        logger.info(f"Generating billing report for customer {customer_id} from {start_date} to {end_date}")
        
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
        # Create calculator and generate report
        calculator = BillingCalculator(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        report = calculator.generate_report()
        
        # Return in requested format
        if output_format == 'json':
            return calculator.to_json()
        elif output_format == 'csv':
            return calculator.to_csv()
        elif output_format == 'dict':
            return calculator.to_dict()
        else:
            raise ValidationError(f"Unsupported output format: {output_format}")
            
    except Exception as e:
        logger.error(f"Error generating billing report: {str(e)}")
        raise