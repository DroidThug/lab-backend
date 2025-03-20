from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'reg_no', 'department', 'is_active')
    list_filter = UserAdmin.list_filter + ('role', 'department', 'is_staff', 'is_active')
    
    # Customize the fieldsets to include all our custom fields
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'dob')}),
        ('Academic/Work info', {'fields': ('role', 'designation', 'reg_no', 'department', 'year', 'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Customize the add form fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'department', 'reg_no')
        }),
    )
    
    search_fields = ('username', 'email', 'first_name', 'last_name', 'reg_no', 'department', 'phone_number')
    ordering = ['username', 'email']

admin.site.register(CustomUser, CustomUserAdmin)
