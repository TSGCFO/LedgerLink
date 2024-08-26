from django.contrib import admin
from django import forms
from rules.models import RuleGroup, Rule

class RuleInline(admin.TabularInline):
    model = Rule
    extra = 1
    fields = ['field', 'operator', 'value', 'adjustment_amount']
    readonly_fields = ['adjustment_amount']
    show_change_link = True

    # Overriding the formfield_for_dbfield method to adjust the 'value' field dynamically
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'value' and 'field' in request.GET:
            field_value = request.GET.get('field')
            operator_value = request.GET.get('operator')

            # Handle dynamic adjustments based on both field and operator
            if field_value == 'sku_quantity':
                if operator_value in ['contains', 'in', 'ni']:
                    formfield = forms.CharField(
                        widget=forms.Textarea,
                        help_text='Enter the SKUs in a list format, separated by semicolons.'
                    )
                elif operator_value in ['eq', 'ne']:
                    formfield = forms.CharField(
                        help_text='Enter the SKU in a JSON format.'
                    )
            elif field_value in ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']:
                formfield = forms.DecimalField(
                    help_text='Enter a numeric value.',
                    min_value=0
                )
            else:
                formfield = forms.CharField(
                    help_text='Enter the condition value.'
                )
        return formfield

class RuleGroupAdmin(admin.ModelAdmin):
    list_display = ['customer_service', 'logic_operator']
    search_fields = ['customer_service__customer__company_name', 'logic_operator']
    list_filter = ['logic_operator', 'customer_service__customer__company_name']
    inlines = [RuleInline]

admin.site.register(RuleGroup, RuleGroupAdmin)
