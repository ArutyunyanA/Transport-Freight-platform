from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import JSONField
from users.models import ShipperProfile, CarrierProfile

class CargoCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class TransportCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class CargoOrder(models.Model):
    TRAILER_TYPES = (
        ('tautliner', 'Tautliner'),
        ('reefer', 'Reefer'),
        ('insulated trailer', 'Insulated Trailer'),
        ('container chassis', 'Container chassis'),
        ('flatbed trailer', 'Flatbed trailer'),
        ('tandem trailer', 'Tandem trailer'),
        ('car transporter', 'Car transporter'),
        ('cattle trailer', 'Cattle trailer'),
        ('open-top trailer', 'Open-top trailer'),
        ('cement tanker', 'Cememnt tanker'),
        ('adr', 'ADR'),
        ('timber trailer', 'Timber trailer'),
        ('lowboy trailer', 'Lowboy trailer'),
        ('tanker trailer', 'Tanker trailer'),
        ('dump trailer', 'Dump trailer'),
        ('bulk flour tanker', 'Bulk flour tanker'),
    )
    shipper = models.ForeignKey(ShipperProfile, on_delete=models.CASCADE, related_name="cargo_orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cargo_item = models.ManyToManyField('orders.CargoItem', related_name="cargo_orders")
    loading_points = models.JSONField(default=list, help_text="List of loading points with city, address and post code")
    unloading_points = models.JSONField(default=list, help_text="List of unloading points with city, address and post code")
    insurance = models.BooleanField(default=False, help_text="Cargo Insurance")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator], help_text="Freight cost")
    categories = models.ManyToManyField(CargoCategory, blank=True, related_name="cargo_orders")
    is_accepted = models.BooleanField(default=False)
    route_info = models.JSONField(blank=True, null=True, help_text="Информация о маршруте (расстояние, время, геометрия)")
    carrier = models.ForeignKey(CarrierProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="accepted_orders")

    trailer_type = models.CharField(
        max_length=50,
        choices=TRAILER_TYPES,
        blank=True,
        null=True,
        help_text="Required trailer type",
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at'])
        ]

    def __str__(self):
        return f"CargoOrder #{self.pk} from {self.shipper.user.company_name}"

class CargoItem(models.Model):
    shipper = models.ForeignKey(ShipperProfile, on_delete=models.CASCADE, related_name="cargo_items")
    name = models.CharField(max_length=255, help_text="Cargo name")
    volume = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Available volume in (m³)")
    weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Total weight in (kg)")
    on_pallets = models.BooleanField(default=False, help_text="Stored on pallets")
    number_of_pallets = models.PositiveIntegerField(default=0, help_text="Number of pallets")
    packaging = models.CharField(max_length=255, blank=True, null=True, help_text="Packaging type (e.g, boxes, barrels)")
    storage_conditions = models.TextField(blank=True, null=True, help_text="Special storage conditions")
    transport_conditions = models.TextField(blank=True, null=True, help_text="Required transport conditions")

    def __str__(self):
        return f"{self.name} ({self.volume}, {self.weight})"

class VirtualWarehouse(models.Model):
    shipper = models.OneToOneField(ShipperProfile, on_delete=models.CASCADE, related_name="warehouse")
    items = models.ManyToManyField(CargoItem, through="WarehouseStock")

    def update_stock(self):
        # Получаем все заказы с их элементами
        orders = CargoOrder.objects.filter(shipper=self.shipper).prefetch_related('cargo_item')

        # Обновляем остатки по каждому товару на складе
        for stock in self.warehousestock_set.select_related('item'):
            # Суммируем общий вес отгруженного товара
            shipped_amount = sum(
                order_item.weight 
                for order in orders 
                for order_item in order.cargo_item.all() 
                if order_item == stock.item
            )
            # Обновляем остаток
            stock.available_quantity = max(stock.initial_quantity - shipped_amount, 0)
            stock.save()

    def __str__(self):
        return f"Warehouse of {self.shipper.user.company_name}"


class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(VirtualWarehouse, on_delete=models.CASCADE)
    item = models.ForeignKey('orders.CargoItem', on_delete=models.CASCADE)
    initial_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.item} in {self.warehouse}"


    def __str__(self):
        return f"{self.item.name}: {self.available_quantity} available for freight"

class TransportOrder(models.Model):
    carrier = models.ForeignKey('users.CarrierProfile', on_delete=models.CASCADE, related_name="transport_orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transport_items = models.ManyToManyField('orders.TransportItem', related_name="transport_orders")
    insurance = models.BooleanField(default=False, help_text="Cargo Insurance")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator], help_text="Freight cost")
    categories = models.ManyToManyField(TransportCategory, blank=True, related_name="transport_orders")
    loading_points = models.JSONField(default=list, help_text="List of loading points with city, address and post code")
    unloading_points = models.JSONField(default=list, help_text="List of unloading points with city, address and post code")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at'])
        ]
    
    def __str__(self):
        return f"TransportOrder #{self.pk} from {self.carrier.user.company_name}"


class TransportItem(models.Model):
    carrier = models.ForeignKey(CarrierProfile, on_delete=models.CASCADE, related_name="transport_items")
    driver_license = models.CharField(max_length=20, unique=True, help_text="Driver license number")
    truck_number = models.CharField(max_length=20, unique=True, help_text="Truck license plate")
    trailer_number = models.CharField(max_length=20, unique=True, help_text="Trailer license plate")
    trailer_type = models.CharField(
        max_length=50,
        choices=[
            ('tautliner', 'Tautliner'),
            ('reefer', 'Reefer'),
            ('insulated trailer', 'Insulated Trailer'),
            ('container chassis', 'Container chassis'),
            ('flatbed trailer', 'Flatbed trailer'),
            ('tandem trailer', 'Tandem trailer'),
            ('car transporter', 'Car transporter'),
            ('cattle trailer', 'Cattle trailer'),
            ('open-top trailer', 'Open-top trailer'),
            ('cement tanker', 'Cememnt tanker'),
            ('adr', 'ADR'),
            ('timber trailer', 'Timber trailer'),
            ('lowboy trailer', 'Lowboy trailer'),
            ('tanker trailer', 'Tanker trailer'),
            ('dump trailer', 'Dump trailer'),
            ('bulk flour tanker', 'Bulk flour tanker'),
        ],
        help_text="Type of trailer"
    )

    def __str__(self):
        return f"{self.truck_number} - {self.trailer_type}"


class ShipmentContract(models.Model):
    cargo_order = models.ForeignKey(CargoOrder, on_delete=models.CASCADE, related_name="contracts")
    transport_order = models.ForeignKey(TransportOrder, on_delete=models.CASCADE, related_name="contracts")
    contract_number = models.CharField(max_length=50, unique=True, help_text="Unique number of contract")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Freight cost")
    payment_deadline = models.DateTimeField(help_text="Deadline of payment")
    delivery_deadline = models.DateTimeField(help_text="Delivery dealine")
    accepted = models.BooleanField(default=False, help_text="The contract was accepted by both parties")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'])
        ]

    def __str__(self):
        return f"Contract {self.contract_number}"

class CMRDocument(models.Model):
    contract = models.ForeignKey(ShipmentContract, on_delete=models.CASCADE, related_name="cmr_documents")
    pdf_file = models.FileField(upload_to='cmr_documents/', help_text="PDF-file CMR")
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['-generated_at'])
        ]

    def __str__(self):
        return f"CMR for Contract {self.contract.contract_number}"