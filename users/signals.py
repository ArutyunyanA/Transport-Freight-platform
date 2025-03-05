from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from geodata.models import get_coordinate_async
import asyncio
from asgiref.sync import async_to_sync
from .models import CustomUser, ShipperProfile, CarrierProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'shipper':
            ShipperProfile.objects.create(
                user=instance,
                legal_address=instance.address,  # Берём данные из CustomUser
                contact_person=instance.contact_person,
                phone_number=instance.phone_number,
                email=instance.email,
                vat_number=instance.vat_number
            )
        elif instance.user_type == 'carrier':
            CarrierProfile.objects.create(
                user=instance,
                legal_address=instance.address,
                contact_person=instance.contact_person,
                phone_number=instance.phone_number,
                email=instance.email,
                vat_number=instance.vat_number
            )

@receiver(pre_save, sender=ShipperProfile)
def update_shipper_location(sender, instance, **kwargs):
    if instance.legal_address:
        # Здесь мы должны запустить асинхронную функцию синхронно – это можно сделать через asyncio.run,
        # но будьте осторожны с этим в сигналах (это может повлиять на производительность).
        location = asyncio.run(get_coordinate_async(instance.legal_address))
        if location and isinstance(location, list) and len(location) >= 2:
            # Если у вас нет полного адреса, можно оставить поле legal_address без изменений
            instance.legal_address_latitude = location[1]
            instance.legal_address_longitude = location[0]
    # Аналогично можно обработать warehouse_address, если это необходимо
    if instance.warehouse_address:
        location = asyncio.run(get_coordinate_async(instance.warehouse_address))
        if location and isinstance(location, list) and len(location) >= 2:
            instance.warehouse_latitude = location[1]
            instance.warehouse_longitude = location[0]



@receiver(pre_save, sender=CarrierProfile)
def update_carrier_location(sender, instance, **kwargs):
    if instance.legal_address:
        location = asyncio.run(get_coordinate_async(instance.legal_address))
        if location and isinstance(location, list) and len(location) >= 2:
            instance.legal_address_latitude = location[1]
            instance.legal_address_longitude = location[0]
