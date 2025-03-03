#!/bin/bash

# Install Python development headers if needed
echo "Installing Python development headers (may require your password)..."
sudo zypper install -y python3-devel gcc

# Install pure Python packages first
echo "Installing pure Python packages..."
pip install -r pure_python_requirements.txt

# Install compiled packages with binary preference
echo "Installing compiled packages (with binary preference)..."
pip install --prefer-binary -r compiled_requirements.txt

# If you still have issues, try installing individual packages from compiled_requirements.txt
echo "If you had errors above, you can try installing individual packages:"
echo "pip install --prefer-binary numpy pandas pillow"

# Instructions for database configuration
echo ""
echo "PostgreSQL adapter installation may fail. If so, modify your Django settings.py:"
echo ""
echo "DATABASES = {"
echo "    'default': {"
echo "        'ENGINE': 'django.db.backends.sqlite3',"
echo "        'NAME': BASE_DIR / 'db.sqlite3',"
echo "    }"
echo "}"
echo ""
echo "Installation complete. Check above for any errors."