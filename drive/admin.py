from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Entity

# Registering the User model in the Django admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']  # Display these fields in the admin list view
    search_fields = ['name', 'email']  # Add search functionality for these fields
    list_filter = ['name']  # Add filters on name in the list view

# Registering the Entity model in the Django admin
@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'folder_path', 'content_type', 'is_folder', 'parent_folder', 'url']  # Customize the fields to display
    search_fields = ['name', 'folder_path']  # Add search functionality
    list_filter = ['is_folder']  # Filter based on whether it's a folder or not