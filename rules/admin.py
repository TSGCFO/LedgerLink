from django.contrib import admin
from rules.models import RuleGroup, Rule


class RuleInline(admin.TabularInline):
    model = Rule
    extra = 1  # Number of empty rule forms displayed by default
    fields = ['field', 'operator', 'value', 'adjustment_amount']
    readonly_fields = ['adjustment_amount']  # If you want the adjustment_amount to be non-editable in some cases
    show_change_link = True


class RuleGroupAdmin(admin.ModelAdmin):
    list_display = ['customer_service', 'logic_operator']
    search_fields = ['customer_service__customer__company_name', 'logic_operator']
    list_filter = ['logic_operator', 'customer_service__customer__company_name']
    inlines = [RuleInline]


admin.site.register(RuleGroup, RuleGroupAdmin)
