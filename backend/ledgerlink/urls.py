from django.contrib import admin
from django.urls import path, include
from billing.views import home  # Import the home view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('billing.urls')),  # Include billing URLs
    path('', home, name='home'),  # Add this line to handle the root URL
]
