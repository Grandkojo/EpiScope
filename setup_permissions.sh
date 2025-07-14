#!/bin/bash

# EpiScope Permission System Setup Script
# This script sets up the complete permission system for the EpiScope project

echo "=========================================="
echo "EpiScope Permission System Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

echo "Step 1: Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Step 2: Setting up permission groups..."
python manage.py setup_permissions

echo "Step 3: Creating default groups..."
python manage.py shell -c "
from api.utils import create_default_user_groups
result = create_default_user_groups()
print('Groups :', result)
"

echo "Step 4: Checking current users..."
python manage.py manage_users list

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Create admin users: python manage.py manage_users promote --username <username>"
echo "3. Check permissions: python manage.py manage_users check --username <username>"
echo ""
echo "Available management commands:"
echo "- python manage.py setup_permissions (re-run permission setup)"
echo "- python manage.py manage_users list (list all users)"
echo "- python manage.py manage_users promote --username <username> (promote to admin)"
echo "- python manage.py manage_users demote --username <username> (demote from admin)"
echo "- python manage.py manage_users check --username <username> (check user permissions)"
echo "- python manage.py manage_users groups (list all groups)"
echo ""
echo "For more information, see PERMISSIONS_GUIDE.md" 