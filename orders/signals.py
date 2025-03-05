from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CargoOrder, VirtualWarehouse
from users.models import ShipperProfile

@receiver(post_save, sender=ShipperProfile)
def create_warehouse(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'warehouse'):
        VirtualWarehouse.objects.create(shipper=instance)

@receiver(post_save, sender=CargoOrder)
def update_warehouse_stock(sender, instance, **kwargs):
    if instance.shipper.warehouse_address:
        instance.shipper.warehouse.update_stock()