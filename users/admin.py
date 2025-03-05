from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ShipperProfile, CarrierProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'company_name', 'user_type', 'vat_number', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'company_name', 'vat_number')
    ordering = ('company_name',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'company_name', 'contact_person', 'phone_number', 'vat_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Importent Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'company_name', 'user_type', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

@admin.register(ShipperProfile)
class ShipperProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'legal_address', 'warehouse_address', 'vat_number')
    search_fields = ('user__company_name', 'vat_number')
    list_filter = ('user__user_type',)


@admin.register(CarrierProfile)
class CarrierProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'legal_address', 'vat_number')
    search_fields = ('user__company_name', 'vat_number')
    list_filter = ('user__user_type',)
