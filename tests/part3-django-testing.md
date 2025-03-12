# Django Backend Testing

This section covers comprehensive testing strategies for your Django backend, focusing on models, views, forms, APIs, and more. Let's dive into each aspect of Django testing with detailed examples.

## Table of Contents

1. [Model Testing](#model-testing)
2. [View Testing](#view-testing)
3. [Form Testing](#form-testing)
4. [API Testing](#api-testing)
5. [Template Testing](#template-testing)
6. [URL Testing](#url-testing)
7. [Authentication and Permission Testing](#authentication-and-permission-testing)
8. [Management Command Testing](#management-command-testing)
9. [Signal Testing](#signal-testing)
10. [Advanced Testing Techniques](#advanced-testing-techniques)

## Model Testing

Model tests ensure your database models behave correctly, including validations, methods, and relationships.

### Basic Model Testing

Let's start with a sample model for a task management app:

```python
# tasks/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_tasks'
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        if not self.due_date:
            return False
        return self.due_date < timezone.now().date() and self.status != 'completed'
    
    def mark_completed(self):
        self.status = 'completed'
        self.save()
    
    class Meta:
        ordering = ['-created_at']
```

Now, let's write tests for this model:

```python
# tasks/tests/test_models.py
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from tasks.models import Task

User = get_user_model()

class TaskModelTest(TestCase):
    def setUp(self):
        # This runs before each test method
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            assigned_to=self.user,
            created_by=self.user
        )
    
    def test_task_creation(self):
        # Verify the task is created with expected values
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is a test task')
        self.assertEqual(self.task.status, 'pending')  # Default value
        self.assertEqual(self.task.assigned_to, self.user)
        self.assertEqual(self.task.created_by, self.user)
        self.assertIsNone(self.task.due_date)
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)
    
    def test_task_string_representation(self):
        # Verify the string representation
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_ordering(self):
        # Create a newer task
        newer_task = Task.objects.create(
            title='Newer Task',
            assigned_to=self.user,
            created_by=self.user
        )
        
        # Verify ordering (newest first)
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], newer_task)
        self.assertEqual(tasks[1], self.task)
    
    def test_is_overdue_method_with_no_due_date(self):
        # Task with no due date should not be overdue
        self.assertFalse(self.task.is_overdue())
    
    def test_is_overdue_method_with_future_due_date(self):
        # Task with future due date should not be overdue
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.task.due_date = tomorrow
        self.task.save()
        
        self.assertFalse(self.task.is_overdue())
    
    def test_is_overdue_method_with_past_due_date(self):
        # Task with past due date should be overdue
        yesterday = timezone.now().date() - timedelta(days=1)
        self.task.due_date = yesterday
        self.task.save()
        
        self.assertTrue(self.task.is_overdue())
    
    def test_is_overdue_method_with_past_due_date_but_completed(self):
        # Completed task should not be overdue even with past due date
        yesterday = timezone.now().date() - timedelta(days=1)
        self.task.due_date = yesterday
        self.task.status = 'completed'
        self.task.save()
        
        self.assertFalse(self.task.is_overdue())
    
    def test_mark_completed_method(self):
        # Verify the method updates the status
        self.assertEqual(self.task.status, 'pending')
        self.task.mark_completed()
        self.assertEqual(self.task.status, 'completed')
        
        # Verify it was saved to the database
        refreshed_task = Task.objects.get(id=self.task.id)
        self.assertEqual(refreshed_task.status, 'completed')
```

### Using Model Factories

To simplify creating test objects, let's use factory_boy:

```python
# tasks/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True

class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
    
    title = factory.Sequence(lambda n: f'Task {n}')
    description = factory.Faker('paragraph')
    status = 'pending'
    assigned_to = factory.SubFactory(UserFactory)
    created_by = factory.SelfAttribute('assigned_to')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    
    # Traits for different types of tasks
    class Params:
        overdue = factory.Trait(
            due_date=factory.LazyFunction(
                lambda: timezone.now().date() - timedelta(days=1)
            )
        )
        
        due_soon = factory.Trait(
            due_date=factory.LazyFunction(
                lambda: timezone.now().date() + timedelta(days=1)
            )
        )
        
        completed = factory.Trait(
            status='completed'
        )
```

Now let's rewrite our tests using these factories:

```python
# tasks/tests/test_models_with_factories.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from .factories import UserFactory, TaskFactory

class TaskModelWithFactoriesTest(TestCase):
    def test_task_creation(self):
        # Create a task using the factory
        task = TaskFactory()
        
        # Verify it was created correctly
        self.assertIsNotNone(task.title)
        self.assertIsNotNone(task.description)
        self.assertEqual(task.status, 'pending')
        self.assertIsNotNone(task.assigned_to)
        self.assertEqual(task.created_by, task.assigned_to)
    
    def test_is_overdue_with_traits(self):
        # Create overdue task
        overdue_task = TaskFactory(overdue=True)
        self.assertTrue(overdue_task.is_overdue())
        
        # Create completed overdue task
        completed_overdue_task = TaskFactory(overdue=True, completed=True)
        self.assertFalse(completed_overdue_task.is_overdue())
        
        # Create task due soon
        due_soon_task = TaskFactory(due_soon=True)
        self.assertFalse(due_soon_task.is_overdue())
    
    def test_task_relationships(self):
        # Create a user
        user = UserFactory()
        
        # Create tasks assigned to this user
        tasks = TaskFactory.create_batch(5, assigned_to=user, created_by=user)
        
        # Verify the relationship
        self.assertEqual(user.assigned_tasks.count(), 5)
        self.assertEqual(user.created_tasks.count(), 5)
```

### Testing Model Validators

Let's add some custom validation to our task model and test it:

```python
# Update tasks/models.py to add validation
from django.core.exceptions import ValidationError

class Task(models.Model):
    # ... existing fields ...
    
    def clean(self):
        if self.status == 'completed' and not self.assigned_to:
            raise ValidationError("Completed tasks must have an assignee.")
        
        if self.due_date and self.due_date < self.created_at.date():
            raise ValidationError("Due date cannot be in the past.")

# Now test the validation
# tasks/tests/test_models.py - add new tests
def test_completed_task_requires_assignee(self):
    # Create a task without assignee
    task = Task(
        title='No Assignee Task',
        status='completed',
        created_by=self.user
    )
    
    # Validation should fail
    with self.assertRaises(ValidationError):
        task.full_clean()
    
    # Fix it by adding assignee
    task.assigned_to = self.user
    task.full_clean()  # Should not raise exception

def test_due_date_cannot_be_in_past(self):
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Create a task with past due date
    task = Task(
        title='Past Due Task',
        assigned_to=self.user,
        created_by=self.user,
        due_date=yesterday
    )
    
    # Validation should fail
    with self.assertRaises(ValidationError):
        task.full_clean()
    
    # Fix it with future date
    tomorrow = timezone.now().date() + timedelta(days=1)
    task.due_date = tomorrow
    task.full_clean()  # Should not raise exception
```

## View Testing

View tests ensure your views render the correct templates, process form data correctly, and return appropriate responses.

### Testing Function-Based Views

Let's test a simple function-based view:

```python
# tasks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm

@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form})
```

Now let's test these views:

```python
# tasks/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tasks.models import Task
from .factories import UserFactory, TaskFactory

User = get_user_model()

class TaskViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = UserFactory()
        self.client = Client()
        
        # Log in the test user
        self.client.login(username=self.user.username, password='password123')
        
        # Create some test tasks
        self.tasks = TaskFactory.create_batch(3, assigned_to=self.user, created_by=self.user)
        
        # Create a task assigned to another user
        other_user = UserFactory()
        self.other_task = TaskFactory(assigned_to=other_user, created_by=self.user)
    
    def test_task_list_view(self):
        # Get the task list page
        url = reverse('task_list')
        response = self.client.get(url)
        
        # Check the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check the right template is used
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        
        # Check the context contains our tasks
        tasks_in_context = response.context['tasks']
        self.assertEqual(tasks_in_context.count(), 3)
        
        # Check the other user's task is not included
        self.assertNotIn(self.other_task, tasks_in_context)
    
    def test_task_detail_view(self):
        # Get the task detail page
        url = reverse('task_detail', args=[self.tasks[0].pk])
        response = self.client.get(url)
        
        # Check the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check the right template is used
        self.assertTemplateUsed(response, 'tasks/task_detail.html')
        
        # Check the context contains our task
        task_in_context = response.context['task']
        self.assertEqual(task_in_context, self.tasks[0])
    
    def test_task_create_view_get(self):
        # Get the task create page
        url = reverse('task_create')
        response = self.client.get(url)
        
        # Check the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check the right template is used
        self.assertTemplateUsed(response, 'tasks/task_form.html')
        
        # Check the form is in the context
        self.assertIn('form', response.context)
    
    def test_task_create_view_post(self):
        # Count tasks before creating
        task_count_before = Task.objects.count()
        
        # Submit the form
        url = reverse('task_create')
        form_data = {
            'title': 'New Test Task',
            'description': 'Created in a test',
            'status': 'pending',
            'assigned_to': self.user.pk
        }
        response = self.client.post(url, form_data)
        
        # Check that a new task was created
        self.assertEqual(Task.objects.count(), task_count_before + 1)
        
        # Check the new task's data
        new_task = Task.objects.latest('created_at')
        self.assertEqual(new_task.title, 'New Test Task')
        self.assertEqual(new_task.created_by, self.user)
        
        # Check we're redirected to the task detail
        self.assertRedirects(response, reverse('task_detail', args=[new_task.pk]))
    
    def test_login_required(self):
        # Log out
        self.client.logout()
        
        # Try to access the task list
        url = reverse('task_list')
        response = self.client.get(url)
        
        # Check we're redirected to login
        login_url = reverse('login')
        self.assertRedirects(
            response, 
            f'{login_url}?next={url}',
            fetch_redirect_response=False
        )
```

### Testing Class-Based Views

Let's convert our views to class-based views and test them:

```python
# tasks/views.py (class-based version)
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Task
from .forms import TaskForm

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})
```

Now let's test these class-based views:

```python
# tasks/tests/test_class_views.py
from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Task
from .factories import UserFactory, TaskFactory

class TaskClassViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = UserFactory()
        self.client = Client()
        
        # Log in the test user
        self.client.login(username=self.user.username, password='password123')
        
        # Create some test tasks
        self.tasks = TaskFactory.create_batch(3, assigned_to=self.user, created_by=self.user)
    
    def test_task_list_view(self):
        # Get the task list page
        url = reverse('task_list')
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        
        # Check context
        tasks_in_context = response.context['tasks']
        self.assertEqual(tasks_in_context.count(), 3)
    
    def test_task_detail_view(self):
        # Get the task detail page
        url = reverse('task_detail', args=[self.tasks[0].pk])
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_detail.html')
        
        # Check context
        task_in_context = response.context['task']
        self.assertEqual(task_in_context, self.tasks[0])
    
    def test_task_create_view(self):
        # Get the form
        url = reverse('task_create')
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_form.html')
        
        # Submit the form
        form_data = {
            'title': 'New Class-Based View Task',
            'description': 'Created in a test',
            'status': 'pending',
            'assigned_to': self.user.pk
        }
        response = self.client.post(url, form_data)
        
        # Check a new task was created
        new_task = Task.objects.filter(title='New Class-Based View Task').first()
        self.assertIsNotNone(new_task)
        self.assertEqual(new_task.created_by, self.user)
        
        # Check redirection
        self.assertRedirects(response, reverse('task_detail', args=[new_task.pk]))
```

## Form Testing

Form tests verify that forms validate input correctly and save data properly.

Let's create and test a form for our Task model:

```python
# tasks/forms.py
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'assigned_to', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long")
        return title
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        assigned_to = cleaned_data.get('assigned_to')
        
        if status == 'completed' and not assigned_to:
            raise forms.ValidationError("Completed tasks must have an assignee")
        
        return cleaned_data
```

Now let's test this form:

```python
# tasks/tests/test_forms.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tasks.forms import TaskForm
from .factories import UserFactory

class TaskFormTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
    
    def test_valid_form(self):
        # Create valid form data
        form_data = {
            'title': 'Valid Task Title',
            'description': 'This is a valid task',
            'status': 'pending',
            'assigned_to': self.user.pk,
            'due_date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        
        # Create and validate form
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_title_validation(self):
        # Create form with short title
        form_data = {
            'title': 'Test',  # Less than 5 characters
            'status': 'pending',
            'assigned_to': self.user.pk
        }
        
        # Create and validate form
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('at least 5 characters', str(form.errors['title']))
    
    def test_completed_task_assignee_validation(self):
        # Create form for completed task without assignee
        form_data = {
            'title': 'Completed Task',
            'status': 'completed',
            'assigned_to': '',  # No assignee
        }
        
        # Create and validate form
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Completed tasks must have an assignee', str(form.errors))
    
    def test_form_widgets(self):
        # Create form instance
        form = TaskForm()
        
        # Check widget types
        self.assertEqual(form.fields['due_date'].widget.attrs['type'], 'date')
        self.assertEqual(form.fields['description'].widget.attrs['rows'], 4)
    
    def test_form_save(self):
        # Create valid form data
        form_data = {
            'title': 'Task to Save',
            'description': 'This task will be saved',
            'status': 'pending',
            'assigned_to': self.user.pk
        }
        
        # Create and validate form
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form
        task = form.save(commit=False)
        task.created_by = self.user
        task.save()
        
        # Check saved data
        self.assertEqual(task.title, 'Task to Save')
        self.assertEqual(task.assigned_to, self.user)
        self.assertEqual(task.created_by, self.user)
```

## API Testing

API tests verify that your API endpoints work correctly, handling requests and returning appropriate responses.

Let's create a REST API for our tasks using Django REST Framework:

```python
# tasks/serializers.py
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 
            'assigned_to', 'assigned_to_username',
            'created_by', 'created_by_username',
            'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

# tasks/api.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

class IsOwnerOrAssignee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (obj.created_by == request.user or 
                obj.assigned_to == request.user)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAssignee]
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assigned_to=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        task = self.get_object()
        task.mark_completed()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
```

Now let's test this API:

```python
# tasks/tests/test_api.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from tasks.models import Task
from .factories import UserFactory, TaskFactory

class TaskAPITests(APITestCase):
    def setUp(self):
        # Create users
        self.user = UserFactory()
        self.other_user = UserFactory()
        
        # Set up client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create tasks
        self.tasks = TaskFactory.create_batch(3, assigned_to=self.user, created_by=self.user)
        self.other_user_task = TaskFactory(assigned_to=self.other_user, created_by=self.user)
        
        # API endpoints
        self.list_url = reverse('api:task-list')
        self.detail_url = reverse('api:task-detail', args=[self.tasks[0].id])
        self.complete_url = reverse('api:task-mark-completed', args=[self.tasks[0].id])
    
    def test_get_task_list(self):
        # Get task list
        response = self.client.get(self.list_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return tasks assigned to user
        self.assertEqual(len(response.data), 3)
        task_ids = [task['id'] for task in response.data]
        self.assertNotIn(self.other_user_task.id, task_ids)
    
    def test_get_task_detail(self):
        # Get task detail
        response = self.client.get(self.detail_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.tasks[0].title)
        self.assertEqual(response.data['created_by_username'], self.user.username)
    
    def test_create_task(self):
        # Task data
        data = {
            'title': 'API Test Task',
            'description': 'Created through the API',
            'status': 'pending',
            'assigned_to': self.user.id
        }
        
        # Create task
        response = self.client.post(self.list_url, data)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check task was created
        self.assertTrue(Task.objects.filter(title='API Test Task').exists())
        new_task = Task.objects.get(title='API Test Task')
        self.assertEqual(new_task.created_by, self.user)
    
    def test_update_task(self):
        # New data
        data = {
            'title': 'Updated Task',
            'description': self.tasks[0].description,
            'status': self.tasks[0].status,
            'assigned_to': self.user.id
        }
        
        # Update task
        response = self.client.put(self.detail_url, data)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check task was updated
        self.tasks[0].refresh_from_db()
        self.assertEqual(self.tasks[0].title, 'Updated Task')
    
    def test_mark_completed_action(self):
        # Initial status should be pending
        self.assertEqual(self.tasks[0].status, 'pending')
        
        # Call mark_completed action
        response = self.client.post(self.complete_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check task was marked as completed
        self.tasks[0].refresh_from_db()
        self.assertEqual(self.tasks[0].status, 'completed')
    
    def test_permission_other_user_task(self):
        # Try to access other user's task
        other_task_url = reverse('api:task-detail', args=[self.other_user_task.id])
        response = self.client.get(other_task_url)
        
        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unauthenticated_access(self):
        # Logout
        self.client.force_authenticate(user=None)
        
        # Try to access API
        response = self.client.get(self.list_url)
        
        # Should be unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

## Template Testing

Template tests verify that your templates render correctly with the provided context.

Let's test a task list template:

```html
<!-- tasks/templates/tasks/task_list.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Your Tasks</h1>
  
  {% if tasks %}
    <ul id="task-list">
      {% for task in tasks %}
        <li class="task-item {% if task.is_overdue %}overdue{% endif %}">
          <a href="{% url 'task_detail' task.id %}">{{ task.title }}</a>
          <span class="task-status {{ task.status }}">{{ task.get_status_display }}</span>
          {% if task.due_date %}
            <span class="due-date">Due: {{ task.due_date|date:"M d, Y" }}</span>
          {% endif %}
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>No tasks found.</p>
  {% endif %}
  
  <a href="{% url 'task_create' %}" class="button">New Task</a>
{% endblock %}
```

Now let's test this template:

```python
# tasks/tests/test_templates.py
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .factories import UserFactory, TaskFactory

class TaskTemplateTests(TestCase):
    def setUp(self):
        # Create user and login
        self.user = UserFactory()
        self.client.force_login(self.user)
        
        # Create normal task
        self.task = TaskFactory(
            title="Normal Task",
            assigned_to=self.user,
            created_by=self.user
        )
        
        # Create overdue task
        yesterday = timezone.now().date() - timedelta(days=1)
        self.overdue_task = TaskFactory(
            title="Overdue Task",
            assigned_to=self.user,
            created_by=self.user,
            due_date=yesterday
        )
    
    def test_task_list_template(self):
        # Get task list page
        url = reverse('task_list')
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        
        # Check context
        self.assertIn('tasks', response.context)
        
        # Check content
        content = response.content.decode()
        
        # Check page structure
        self.assertIn('<h1>Your Tasks</h1>', content)
        self.assertIn('<ul id="task-list">', content)
        
        # Check tasks are listed
        self.assertIn('Normal Task', content)
        self.assertIn('Overdue Task', content)
        
        # Check overdue class
        self.assertIn('class="task-item overdue"', content)
        
        # Check link to create new task
        self.assertIn('href="{}"'.format(reverse('task_create')), content)
    
    def test_empty_task_list_template(self):
        # Delete all tasks
        self.task.delete()
        self.overdue_task.delete()
        
        # Get task list page
        url = reverse('task_list')
        response = self.client.get(url)
        
        # Check content
        content = response.content.decode()
        self.assertIn('No tasks found.', content)
        self.assertNotIn('<ul id="task-list">', content)
```

## URL Testing

URL tests verify that your URLs resolve to the correct views.

```python
# tasks/tests/test_urls.py
from django.test import TestCase
from django.urls import reverse, resolve
from tasks.views import TaskListView, TaskDetailView, TaskCreateView

class TaskURLTests(TestCase):
    def test_task_list_url(self):
        url = reverse('task_list')
        self.assertEqual(url, '/tasks/')
        
        resolver = resolve('/tasks/')
        self.assertEqual(resolver.func.__name__, TaskListView.as_view().__name__)
    
    def test_task_detail_url(self):
        url = reverse('task_detail', args=[1])
        self.assertEqual(url, '/tasks/1/')
        
        resolver = resolve('/tasks/1/')
        self.assertEqual(resolver.func.__name__, TaskDetailView.as_view().__name__)
    
    def test_task_create_url(self):
        url = reverse('task_create')
        self.assertEqual(url, '/tasks/create/')
        
        resolver = resolve('/tasks/create/')
        self.assertEqual(resolver.func.__name__, TaskCreateView.as_view().__name__)
```

## Authentication and Permission Testing

These tests verify that your views enforce authentication and permission requirements.

```python
# tasks/tests/test_permissions.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .factories import UserFactory, TaskFactory

class TaskPermissionTests(TestCase):
    def setUp(self):
        # Create users
        self.owner = UserFactory()
        self.assignee = UserFactory()
        self.unrelated_user = UserFactory()
        
        # Create task
        self.task = TaskFactory(
            created_by=self.owner,
            assigned_to=self.assignee
        )
        
        # Set up URLs
        self.detail_url = reverse('task_detail', args=[self.task.id])
        self.api_detail_url = reverse('api:task-detail', args=[self.task.id])
    
    def test_task_detail_view_permissions(self):
        # Unauthenticated user should be redirected to login
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        # Task owner should have access
        self.client.force_login(self.owner)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        
        # Task assignee should have access
        self.client.force_login(self.assignee)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        
        # Unrelated user should not have access (in this case, we'll assume a 403 Forbidden)
        self.client.force_login(self.unrelated_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 403)
    
    def test_api_permissions(self):
        client = APIClient()
        
        # Unauthenticated user should be unauthorized
        response = client.get(self.api_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Task owner should have access
        client.force_authenticate(user=self.owner)
        response = client.get(self.api_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Task assignee should have access
        client.force_authenticate(user=self.assignee)
        response = client.get(self.api_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Unrelated user should not have access
        client.force_authenticate(user=self.unrelated_user)
        response = client.get(self.api_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
```

## Management Command Testing

These tests verify that your custom management commands work correctly.

Let's create a command to clean up old completed tasks:

```python
# tasks/management/commands/cleanup_tasks.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task

class Command(BaseCommand):
    help = 'Delete completed tasks older than a specified number of days'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days old a completed task must be to be deleted'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without actually deleting tasks'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        tasks = Task.objects.filter(
            status='completed',
            updated_at__lt=cutoff_date
        )
        
        count = tasks.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would delete {count} tasks (dry run)')
            )
        else:
            tasks.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} tasks')
            )
```

Now let's test this command:

```python
# tasks/tests/test_commands.py
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from .factories import TaskFactory

class CleanupTasksCommandTest(TestCase):
    def setUp(self):
        # Create old completed tasks (35 days old)
        self.old_date = timezone.now() - timedelta(days=35)
        
        for i in range(3):
            task = TaskFactory(status='completed')
            # Set created_at and updated_at manually to simulate old tasks
            Task.objects.filter(pk=task.pk).update(
                created_at=self.old_date,
                updated_at=self.old_date
            )
        
        # Create recent completed tasks (5 days old)
        self.recent_date = timezone.now() - timedelta(days=5)
        
        for i in range(2):
            task = TaskFactory(status='completed')
            Task.objects.filter(pk=task.pk).update(
                created_at=self.recent_date,
                updated_at=self.recent_date
            )
        
        # Create incomplete tasks
        TaskFactory.create_batch(2, status='pending')
    
    def test_command_with_default_days(self):
        # Capture command output
        out = StringIO()
        call_command('cleanup_tasks', stdout=out)
        
        # Check output
        self.assertIn('Deleted 3 tasks', out.getvalue())
        
        # Check tasks were deleted
        self.assertEqual(Task.objects.count(), 4)  # 2 recent completed + 2 pending
        self.assertEqual(Task.objects.filter(status='completed').count(), 2)
    
    def test_command_with_custom_days(self):
        # Set days to 10, which should delete old tasks (35 days) but keep recent ones (5 days)
        out = StringIO()
        call_command('cleanup_tasks', days=10, stdout=out)
        
        # Check output
        self.assertIn('Deleted 3 tasks', out.getvalue())
        
        # Check tasks were deleted
        self.assertEqual(Task.objects.count(), 4)  # 2 recent completed + 2 pending
    
    def test_command_with_dry_run(self):
        # Use dry run option
        out = StringIO()
        call_command('cleanup_tasks', dry_run=True, stdout=out)
        
        # Check output
        self.assertIn('Would delete 3 tasks (dry run)', out.getvalue())
        
        # Check no tasks were deleted
        self.assertEqual(Task.objects.count(), 7)  # All tasks should remain
```

## Signal Testing

These tests verify that your Django signals work correctly.

Let's create a signal to create a task history entry whenever a task is modified:

```python
# tasks/models.py - add TaskHistory model
class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='task_actions'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

# tasks/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import signals
from .models import Task, TaskHistory

@receiver(post_save, sender=Task)
def create_task_history(sender, instance, created, **kwargs):
    if created:
        TaskHistory.objects.create(
            task=instance,
            action='created',
            details=f'Task "{instance.title}" was created',
            performed_by=instance.created_by
        )
    else:
        TaskHistory.objects.create(
            task=instance,
            action='updated',
            details=f'Task "{instance.title}" was updated',
            performed_by=instance.updated_by if hasattr(instance, 'updated_by') else None
        )

@receiver(signals.pre_save, sender=Task)
def track_status_change(sender, instance, **kwargs):
    # Only run when updating existing instance
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            
            # If status changed, record it
            if old_instance.status != instance.status:
                instance.status_changed = True
                instance.old_status = old_instance.status
            else:
                instance.status_changed = False
        except Task.DoesNotExist:
            pass

@receiver(signals.post_save, sender=Task)
def record_status_change(sender, instance, created, **kwargs):
    # Skip for new instances
    if created:
        return
    
    # If status changed, create a specific history entry
    if getattr(instance, 'status_changed', False):
        TaskHistory.objects.create(
            task=instance,
            action='status_changed',
            details=f'Status changed from "{instance.old_status}" to "{instance.status}"',
            performed_by=instance.updated_by if hasattr(instance, 'updated_by') else None
        )
```

Now let's test these signals:

```python
# tasks/tests/test_signals.py
from django.test import TestCase
from tasks.models import Task, TaskHistory
from .factories import UserFactory, TaskFactory

class TaskSignalsTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
    
    def test_task_creation_signal(self):
        # Before creation, there should be no history
        self.assertEqual(TaskHistory.objects.count(), 0)
        
        # Create a task
        task = TaskFactory(
            title='Signal Test Task',
            created_by=self.user
        )
        
        # Check history was created
        self.assertEqual(TaskHistory.objects.count(), 1)
        
        # Verify history details
        history = TaskHistory.objects.first()
        self.assertEqual(history.task, task)
        self.assertEqual(history.action, 'created')
        self.assertIn('Signal Test Task', history.details)
        self.assertEqual(history.performed_by, self.user)
    
    def test_task_update_signal(self):
        # Create a task first
        task = TaskFactory(created_by=self.user)
        
        # Clear history
        TaskHistory.objects.all().delete()
        
        # Update the task
        task.title = 'Updated Task'
        task.save()
        
        # Check history was created
        self.assertEqual(TaskHistory.objects.count(), 1)
        
        # Verify history details
        history = TaskHistory.objects.first()
        self.assertEqual(history.task, task)
        self.assertEqual(history.action, 'updated')
        self.assertIn('Updated Task', history.details)
    
    def test_status_change_signal(self):
        # Create a task
        task = TaskFactory(
            title='Status Change Task',
            status='pending',
            created_by=self.user
        )
        
        # Clear history
        TaskHistory.objects.all().delete()
        
        # Change status
        task.status = 'in_progress'
        task.updated_by = self.user
        task.save()
        
        # Check histories were created (status_changed + updated)
        self.assertEqual(TaskHistory.objects.count(), 2)
        
        # Verify status change history
        status_history = TaskHistory.objects.filter(action='status_changed').first()
        self.assertIsNotNone(status_history)
        self.assertEqual(status_history.task, task)
        self.assertIn('pending', status_history.details)
        self.assertIn('in_progress', status_history.details)
        self.assertEqual(status_history.performed_by, self.user)
```

## Advanced Testing Techniques

### 1. Parameterized Tests

Use pytest's parameterize to run the same test with different inputs:

```python
# tasks/tests/test_parameterized.py
import pytest
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from .factories import UserFactory, TaskFactory

@pytest.mark.parametrize("status,due_date,expected", [
    # Not due + not completed
    ('pending', None, False),
    # Future + not completed
    ('pending', timezone.now().date() + timedelta(days=1), False),
    # Past + not completed
    ('pending', timezone.now().date() - timedelta(days=1), True),
    # Past + completed
    ('completed', timezone.now().date() - timedelta(days=1), False),
])
def test_is_overdue_parameterized(status, due_date, expected):
    user = UserFactory()
    task = TaskFactory(
        status=status,
        due_date=due_date,
        created_by=user,
        assigned_to=user
    )
    
    assert task.is_overdue() == expected
```

### 2. Performance Testing

Test database query performance to catch N+1 query problems:

```python
# tasks/tests/test_performance.py
from django.test import TestCase
from django.urls import reverse
from django.test.utils import CaptureQueriesContext
from django.db import connection
from .factories import UserFactory, TaskFactory

class TaskPerformanceTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = UserFactory()
        self.client.force_login(self.user)
        
        # Create many tasks
        TaskFactory.create_batch(20, assigned_to=self.user, created_by=self.user)
    
    def test_task_list_query_count(self):
        url = reverse('task_list')
        
        # Capture queries
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            
            # Check response
            self.assertEqual(response.status_code, 200)
            
            # Check query count (should be small and constant)
            query_count = len(context)
            self.assertLessEqual(query_count, 5, 
                                "Too many queries, check for N+1 problems")
            
            # Debug: print queries
            for i, query in enumerate(context):
                print(f"Query {i}: {query['sql']}")
    
    def test_api_task_list_performance(self):
        url = reverse('api:task-list')
        
        # Capture queries
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
            
            # Check response
            self.assertEqual(response.status_code, 200)
            
            # Check query count
            query_count = len(context)
            self.assertLessEqual(query_count, 5,
                                "API should use efficient queries")
```

### 3. Test Data Migrations

Test that your data migrations work correctly:

```python
# tasks/migrations/0002_add_default_statuses.py
from django.db import migrations

def add_default_statuses(apps, schema_editor):
    Task = apps.get_model('tasks', 'Task')
    
    # Update any tasks without a status
    Task.objects.filter(status='').update(status='pending')

def reverse_default_statuses(apps, schema_editor):
    pass  # No need to reverse this migration

class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(add_default_statuses, reverse_default_statuses),
    ]

# tasks/tests/test_migrations.py
from django.test import TestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.apps import apps

class MigrationTests(TestCase):
    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name
    
    def setUp(self):
        # Create the schema for our test
        self.executor = MigrationExecutor(connection)
        self.executor.migrate([('tasks', '0001_initial')])
        
        # Get models
        self.old_apps = self.executor.loader.project_state(('tasks', '0001_initial')).apps
        self.Task = self.old_apps.get_model('tasks', 'Task')
        
        # Create a task with empty status
        self.db_alias = connection.alias
        self.Task.objects.using(self.db_alias).create(
            title='Migration Test Task',
            status=''
        )
    
    def test_default_statuses_migration(self):
        # Verify we have a task with empty status
        tasks = self.Task.objects.using(self.db_alias).all()
        self.assertEqual(tasks.count(), 1)
        self.assertEqual(tasks[0].status, '')
        
        # Run the migration
        self.executor.migrate([('tasks', '0002_add_default_statuses')])
        
        # Get the new state with applied migrations
        self.new_apps = self.executor.loader.project_state(('tasks', '0002_add_default_statuses')).apps
        self.Task = self.new_apps.get_model('tasks', 'Task')
        
        # Check the task has been updated
        tasks = self.Task.objects.using(self.db_alias).all()
        self.assertEqual(tasks.count(), 1)
        self.assertEqual(tasks[0].status, 'pending')
```

### 4. Custom Test Assertions

Create custom test assertions for more readable tests:

```python
# tasks/tests/test_utils.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from .factories import UserFactory, TaskFactory

class TaskTestCase(TestCase):
    def assertTaskIsOverdue(self, task):
        """Assert that a task is overdue."""
        self.assertTrue(
            task.is_overdue(),
            f"Task '{task.title}' should be overdue but isn't."
        )
    
    def assertTaskIsNotOverdue(self, task):
        """Assert that a task is not overdue."""
        self.assertFalse(
            task.is_overdue(),
            f"Task '{task.title}' shouldn't be overdue but is."
        )
    
    def assertTaskHasStatus(self, task, status):
        """Assert that a task has the expected status."""
        self.assertEqual(
            task.status,
            status,
            f"Task '{task.title}' should have status '{status}' but has '{task.status}'."
        )

class TaskCustomAssertionsTest(TaskTestCase):
    def setUp(self):
        self.user = UserFactory()
        
        # Create a task due yesterday
        yesterday = timezone.now().date() - timedelta(days=1)
        self.overdue_task = TaskFactory(
            due_date=yesterday,
            assigned_to=self.user,
            created_by=self.user
        )
        
        # Create a task due tomorrow
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.future_task = TaskFactory(
            due_date=tomorrow,
            assigned_to=self.user,
            created_by=self.user
        )
    
    def test_custom_assertions(self):
        # Test our custom assertions
        self.assertTaskIsOverdue(self.overdue_task)
        self.assertTaskIsNotOverdue(self.future_task)
        
        # Update task status
        self.assertTaskHasStatus(self.overdue_task, 'pending')
        self.overdue_task.mark_completed()
        self.assertTaskHasStatus(self.overdue_task, 'completed')
        
        # Now the task is completed, it shouldn't be overdue
        self.assertTaskIsNotOverdue(self.overdue_task)
```

### 5. Testing for Security Issues

Test that your app is protected against common security issues:

```python
# tasks/tests/test_security.py
from django.test import TestCase, Client
from django.urls import reverse
from .factories import UserFactory, TaskFactory

class SecurityTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = UserFactory()
        self.task = TaskFactory(assigned_to=self.user, created_by=self.user)
    
    def test_csrf_protection(self):
        # Log in
        self.client.login(username=self.user.username, password='password123')
        
        # Try to update without CSRF token
        url = reverse('task_update', args=[self.task.id])
        data = {
            'title': 'CSRF Attack',
            'status': 'completed',
            'assigned_to': self.user.id
        }
        
        response = self.client.post(url, data)
        
        # Should be forbidden
        self.assertEqual(response.status_code, 403)
        
        # Task should not be updated
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, 'CSRF Attack')
    
    def test_xss_prevention(self):
        # Create task with potential XSS payload
        xss_task = TaskFactory(
            title='<script>alert("XSS")</script>',
            assigned_to=self.user,
            created_by=self.user
        )
        
        # Log in
        self.client.login(username=self.user.username, password='password123')
        
        # Visit the task detail page
        url = reverse('task_detail', args=[xss_task.id])
        response = self.client.get(url)
        
        # Response should have escaped the script tags
        content = response.content.decode()
        self.assertIn('&lt;script&gt;', content)
        self.assertNotIn('<script>', content)
    
    def test_sql_injection_prevention(self):
        # Log in
        self.client.login(username=self.user.username, password='password123')
        
        # Try a SQL injection in search
        injection = "'; DROP TABLE auth_user; --"
        url = reverse('task_search') + f'?q={injection}'
        
        # This should not cause an error
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # The user table should still exist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
```

These test examples cover a wide range of testing scenarios for a Django backend. By implementing these tests, you'll have comprehensive test coverage for your Django application, ensuring that it behaves correctly and remains stable as you continue development.
