from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser, Group, Permission



class CustomUser(AbstractUser):
    USER_TYPES = (
        ('shipper', 'Shipper'),
        ('carrier', 'Carrier'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    vat_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    contact_person = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.company_name} ({self.get_user_type_display()})"

class ShipperProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="shipper")
    legal_address = models.CharField(max_length=255)
    legal_address_latitude = models.FloatField(blank=True, null=True)
    legal_address_longitude = models.FloatField(blank=True, null=True)
    warehouse_address = models.OneToOneField('orders.VirtualWarehouse', on_delete=models.SET_NULL, null=True, blank=True)
    warehouse_latitude = models.FloatField(blank=True, null=True)
    warehouse_longitude = models.FloatField(blank=True, null=True)
    contact_person = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    vat_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.company_name} (VAT: {self.vat_number})"


class CarrierProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='carrier')
    legal_address = models.CharField(max_length=255)
    legal_address_latitude = models.FloatField(blank=True, null=True)
    legal_address_longitude = models.FloatField(blank=True, null=True)
    contact_person = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    vat_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.company_name} (VAT: {self.vat_number})"

