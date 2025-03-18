from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

from materials.models import Material, BoxPrice
from materials.tests.factories import MaterialFactory, BoxPriceFactory

User = get_user_model()


class MaterialPermissionTest(TestCase):
    """Test permissions for Material API."""
    
    def setUp(self):
        """Set up test data."""
        # Create materials
        self.material = MaterialFactory(
            name='Test Material',
            description='Test description',
            unit_price=Decimal('10.50')
        )
        
        # Create user roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            is_staff=True
        )
        
        self.standard_user = User.objects.create_user(
            username='standard',
            email='standard@example.com',
            password='standardpass'
        )
        
        self.readonly_user = User.objects.create_user(
            username='readonly',
            email='readonly@example.com',
            password='readonlypass'
        )
        
        # Set up permissions
        material_content_type = ContentType.objects.get_for_model(Material)
        
        # Create a read-only group
        self.readonly_group = Group.objects.create(name='ReadOnly')
        view_material_permission = Permission.objects.get(
            content_type=material_content_type,
            codename='view_material'
        )
        self.readonly_group.permissions.add(view_material_permission)
        self.readonly_user.groups.add(self.readonly_group)
        
        # Create a standard user group with more permissions
        self.standard_group = Group.objects.create(name='Standard')
        change_material_permission = Permission.objects.get(
            content_type=material_content_type,
            codename='change_material'
        )
        add_material_permission = Permission.objects.get(
            content_type=material_content_type,
            codename='add_material'
        )
        self.standard_group.permissions.add(view_material_permission, 
                                           change_material_permission,
                                           add_material_permission)
        self.standard_user.groups.add(self.standard_group)
        
        # URLs
        self.list_url = reverse('material-list')
        self.detail_url = reverse('material-detail', kwargs={'pk': self.material.pk})
        
        # API clients
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)
        
        self.standard_client = APIClient()
        self.standard_client.force_authenticate(user=self.standard_user)
        
        self.readonly_client = APIClient()
        self.readonly_client.force_authenticate(user=self.readonly_user)
        
        self.unauthenticated_client = APIClient()
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access the API."""
        response = self.unauthenticated_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.unauthenticated_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.unauthenticated_client.post(self.list_url, {
            'name': 'New Material',
            'description': 'New description',
            'unit_price': '12.50'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_readonly_user_permissions(self):
        """Test that readonly users can only view materials."""
        # Should be able to view materials
        response = self.readonly_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.readonly_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should not be able to create materials
        response = self.readonly_client.post(self.list_url, {
            'name': 'New Material',
            'description': 'New description',
            'unit_price': '12.50'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Should not be able to update materials
        response = self.readonly_client.put(self.detail_url, {
            'name': 'Updated Material',
            'description': 'Updated description',
            'unit_price': '15.00'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Should not be able to delete materials
        response = self.readonly_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_standard_user_permissions(self):
        """Test that standard users can view, create, and update materials but not delete."""
        # Should be able to view materials
        response = self.standard_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.standard_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be able to create materials
        response = self.standard_client.post(self.list_url, {
            'name': 'New Material',
            'description': 'New description',
            'unit_price': '12.50'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should be able to update materials
        new_material_id = response.data['id']
        new_detail_url = reverse('material-detail', kwargs={'pk': new_material_id})
        
        response = self.standard_client.put(new_detail_url, {
            'name': 'Updated Material',
            'description': 'Updated description',
            'unit_price': '15.00'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should not be able to delete materials without delete permission
        response = self.standard_client.delete(new_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_user_permissions(self):
        """Test that admin users have full access."""
        # Should be able to view materials
        response = self.admin_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.admin_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be able to create materials
        response = self.admin_client.post(self.list_url, {
            'name': 'Admin Material',
            'description': 'Created by admin',
            'unit_price': '20.00'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should be able to update materials
        admin_material_id = response.data['id']
        admin_detail_url = reverse('material-detail', kwargs={'pk': admin_material_id})
        
        response = self.admin_client.put(admin_detail_url, {
            'name': 'Updated Admin Material',
            'description': 'Updated by admin',
            'unit_price': '25.00'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be able to delete materials
        response = self.admin_client.delete(admin_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BoxPriceSecurityTest(TestCase):
    """Test security for BoxPrice API."""
    
    def setUp(self):
        """Set up test data."""
        # Create box prices
        self.box_price = BoxPriceFactory(
            box_type='Standard',
            price=Decimal('5.25'),
            length=Decimal('10.50'),
            width=Decimal('8.25'),
            height=Decimal('6.00')
        )
        
        # Create user with and without authentication
        self.auth_user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='authpass'
        )
        
        # Clients
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.auth_user)
        
        self.unauth_client = APIClient()
        
        # URLs
        self.list_url = reverse('boxprice-list')
        self.detail_url = reverse('boxprice-detail', kwargs={'pk': self.box_price.pk})
    
    def test_authentication_required(self):
        """Test that authentication is required for all endpoints."""
        # List endpoint
        response = self.unauth_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Detail endpoint
        response = self.unauth_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Create endpoint
        response = self.unauth_client.post(self.list_url, {
            'box_type': 'New Box',
            'price': '7.50',
            'length': '12.00',
            'width': '10.00',
            'height': '8.00'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Update endpoint
        response = self.unauth_client.put(self.detail_url, {
            'box_type': 'Updated Box',
            'price': '8.00',
            'length': '12.50',
            'width': '10.50',
            'height': '8.50'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Delete endpoint
        response = self.unauth_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access(self):
        """Test that authenticated users can access all endpoints."""
        # List endpoint
        response = self.auth_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Detail endpoint
        response = self.auth_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create endpoint
        response = self.auth_client.post(self.list_url, {
            'box_type': 'New Box',
            'price': '7.50',
            'length': '12.00',
            'width': '10.00',
            'height': '8.00'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Update endpoint
        new_box_id = response.data['id']
        new_detail_url = reverse('boxprice-detail', kwargs={'pk': new_box_id})
        
        response = self.auth_client.put(new_detail_url, {
            'box_type': 'Updated Box',
            'price': '8.00',
            'length': '12.50',
            'width': '10.50',
            'height': '8.50'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete endpoint
        response = self.auth_client.delete(new_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_injection_protection(self):
        """Test protection against SQL injection attempts."""
        # Test with potentially dangerous input
        malicious_inputs = [
            "'; DROP TABLE materials_boxprice; --",
            "<script>alert('XSS');</script>",
            "UNION SELECT * FROM auth_user--"
        ]
        
        for injection in malicious_inputs:
            response = self.auth_client.post(self.list_url, {
                'box_type': injection,
                'price': '7.50',
                'length': '12.00',
                'width': '10.00',
                'height': '8.00'
            })
            
            # If input validation rejects it, that's fine. If it accepts it,
            # make sure it's treated as a literal string, not executed
            if response.status_code == status.HTTP_201_CREATED:
                box_id = response.data['id']
                box = BoxPrice.objects.get(pk=box_id)
                
                # Verify it's stored as a literal string
                self.assertEqual(box.box_type, injection)
                
                # Verify the database table still exists and has our records
                self.assertTrue(BoxPrice.objects.exists())
    
    def test_max_length_validation(self):
        """Test that field max lengths are enforced."""
        # The box_type field has a max_length of 50
        long_name = 'A' * 100  # 100 characters, well beyond the 50 char limit
        
        response = self.auth_client.post(self.list_url, {
            'box_type': long_name,
            'price': '7.50',
            'length': '12.00',
            'width': '10.00',
            'height': '8.00'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('box_type', response.data)  # Verify the error references the correct field
        
    def test_decimal_field_validation(self):
        """Test validation of decimal fields."""
        # Test exceeding max_digits (10) for price
        response = self.auth_client.post(self.list_url, {
            'box_type': 'Expensive Box',
            'price': '12345678.90',  # 10 digits (should be accepted)
            'length': '12.00',
            'width': '10.00',
            'height': '8.00'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.auth_client.post(self.list_url, {
            'box_type': 'Too Expensive Box',
            'price': '123456789.90',  # 11 digits (should be rejected)
            'length': '12.00',
            'width': '10.00',
            'height': '8.00'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        
        # Test exceeding decimal_places (2) for price
        response = self.auth_client.post(self.list_url, {
            'box_type': 'Precise Box',
            'price': '10.999',  # 3 decimal places (should be rejected)
            'length': '12.00',
            'width': '10.00',
            'height': '8.00'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)