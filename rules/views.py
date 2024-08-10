# rules/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import RuleGroup, Rule
from .forms import RuleGroupForm, RuleForm


def create_rule_group(request):
    if request.method == 'POST':
        form = RuleGroupForm(request.POST)
        if form.is_valid():
            rule_group = form.save()
            return redirect('rule_group_detail', group_id=rule_group.id)
    else:
        form = RuleGroupForm()
    return render(request, 'rules/create_rule_group.html', {'form': form})


def create_rule(request, group_id):
    rule_group = get_object_or_404(RuleGroup, id=group_id)
    if request.method == 'POST':
        form = RuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.rule_group = rule_group
            rule.save()
            return redirect('rule_group_detail', group_id=group_id)
    else:
        form = RuleForm(initial={'rule_group': rule_group})
    return render(request, 'rules/create_rule.html', {'form': form, 'group': rule_group})


def rule_group_list(request):
    rule_groups = RuleGroup.objects.all()
    return render(request, 'rules/rule_group_list.html', {'rule_groups': rule_groups})


def rule_group_detail(request, group_id):
    rule_group = get_object_or_404(RuleGroup, id=group_id)
    rules = rule_group.rules.all()
    return render(request, 'rules/rule_group_detail.html', {'rule_group': rule_group, 'rules': rules})
