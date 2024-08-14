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
            if field_value == 'sku':
                formfield = forms.ChoiceField(choices=[('SKU1', 'SKU1'), ('SKU2', 'SKU2')], help_text='Select the SKU')
            elif field_value in ['quantity', 'case_picks']:
                formfield = forms.IntegerField(min_value=1, help_text='Enter the quantity or number of case picks')
            else:
                formfield = forms.CharField(help_text='Enter the condition value')
        return formfield

class RuleGroupAdmin(admin.ModelAdmin):
    list_display = ['customer_service', 'logic_operator']
    search_fields = ['customer_service__customer__company_name', 'logic_operator']
    list_filter = ['logic_operator', 'customer_service__customer__company_name']
    inlines = [RuleInline]

admin.site.register(RuleGroup, RuleGroupAdmin)
