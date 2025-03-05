from django.contrib import admin
from .models import CargoCategory, CargoItem, TransportItem, CargoOrder, TransportCategory, TransportOrder, ShipmentContract, CMRDocument

@admin.register(CargoItem)
class CargoItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipper', 'volume', 'weight', 'on_pallets', 'storage_conditions')
    search_fields = ('name', 'shipper__user__company_name')
    list_filter = ('on_pallets', 'storage_conditions')


@admin.register(CargoCategory)
class CargoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CargoOrder)
class CargoOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'shipper', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('shipper__user__company_name',)

@admin.register(TransportItem)
class TransportItemAdmin(admin.ModelAdmin):
    list_display = ('truck_number', 'trailer_number', 'driver_license', 'trailer_type', 'carrier')
    search_fields = ('truck_number', 'trailer_number', 'carrier__user__company_name')
    list_filter = ('trailer_type',)

@admin.register(TransportCategory)
class TransportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TransportOrder)
class TransportOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'carrier', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('carrier__user__company_name',)

@admin.register(ShipmentContract)
class ShipmentContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'cargo_order', 'transport_order', 'price', 'accepted')
    search_fields = ('contract_number',)

@admin.register(CMRDocument)
class CMRDocumentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'generated_at')

