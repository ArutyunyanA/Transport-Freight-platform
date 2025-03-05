from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import CargoOrder, TransportOrder, CargoItem, TransportItem, ShipmentContract

class CargoOrderForm(forms.ModelForm):
    # Поля для ввода адресов (эти поля будут использоваться для запроса к API, а потом сохранены координаты)
    loading_address = forms.CharField(
        label='Loading Address',
        widget=forms.TextInput(attrs={'placeholder': 'Insert the loading place'})
    )
    unloading_address = forms.CharField(
        label='Unloading Address',
        widget=forms.TextInput(attrs={'placeholder': 'Insert the unloading place'})
    )
    # Поле цены, которое не является полем модели (его можно обработать в представлении и сохранить в заказе)
    price = forms.DecimalField(
        label='Price',
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter price'})
    )

    class Meta:
        model = CargoOrder
        # Здесь в модель включены только поля, которые пользователь выбирает (выбор товара, страховка, категории, тип прицепа)
        fields = [
            'cargo_item', 'insurance', 'categories', 'trailer_type'
        ]
        widgets = {
            'cargo_item': forms.CheckboxSelectMultiple,
            'categories': forms.CheckboxSelectMultiple,
            'trailer_type': forms.Select,
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Если форма используется грузоотправителем – ограничиваем выбор CargoItem только его объектами
        if user and hasattr(user, 'shipper'):
            self.fields['cargo_item'].queryset = CargoItem.objects.filter(shipper=user.shipper)


class TransportOrderForm(forms.ModelForm):
    loading_address = forms.CharField(
        label='Loading Address',
        widget=forms.TextInput(attrs={'placeholder': 'Insert the loading place'})
    )
    unloading_address = forms.CharField(
        label='Unloading Address',
        widget=forms.TextInput(attrs={'placeholder': 'Insert the unloading place'})
    )

    class Meta:
        model = TransportOrder
        fields = [
            'transport_items', 'insurance', 'categories'
        ]
        widgets = {
            'transport_items': forms.CheckboxSelectMultiple,
            'categories': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Если пользователь является перевозчиком, ограничиваем выбор транспортных единиц только его
        if user and hasattr(user, 'carrier'):
            self.fields['transport_items'].queryset = TransportItem.objects.filter(carrier=user.carrier)
            

class CargoItemForm(forms.ModelForm):
    class Meta:
        model = CargoItem
        fields = [
            'name', 
            'volume', 
            'weight', 
            'on_pallets', 
            'number_of_pallets', 
            'packaging', 
            'storage_conditions', 
            'transport_conditions'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название груза'}),
            'volume': forms.NumberInput(attrs={'placeholder': 'Объём (м³)'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Вес (кг)'}),
            'on_pallets': forms.CheckboxInput(),
            'number_of_pallets': forms.NumberInput(attrs={'placeholder': 'Количество паллет'}),
            'packaging': forms.TextInput(attrs={'placeholder': 'Тип упаковки'}),
            'storage_conditions': forms.Textarea(attrs={'placeholder': 'Условия хранения', 'rows': 3}),
            'transport_conditions': forms.Textarea(attrs={'placeholder': 'Условия транспортировки', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Ожидаем, что в kwargs передается текущий пользователь под ключом 'user'
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Если требуется ограничить выбор элементов только теми, что принадлежат грузоотправителю:
        if user and hasattr(user, 'shipper'):
            self.fields['name'].widget.attrs.update({'readonly': 'readonly'})
            # Если бы у вас было поле с выбором CargoItem, можно было бы:
            # self.fields['cargo_item'].queryset = CargoItem.objects.filter(shipper=user.shipper)

class TransportItemForm(forms.ModelForm):
    class Meta:
        model = TransportItem
        fields = [
            'driver_license', 
            'truck_number', 
            'trailer_number', 
            'trailer_type'
        ]
        widgets = {
            'driver_license': forms.TextInput(attrs={'placeholder': 'Номер водительского удостоверения'}),
            'truck_number': forms.TextInput(attrs={'placeholder': 'Номер грузовика'}),
            'trailer_number': forms.TextInput(attrs={'placeholder': 'Номер прицепа'}),
            'trailer_type': forms.Select(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Если необходимо, можно установить дополнительные ограничения для перевозчика
        # Например, можно сделать поле carrier недоступным для изменения:
        # self.fields['carrier'].disabled = True



class ShipmentContractForm(forms.ModelForm):
    class Meta:
        model = ShipmentContract
        fields = ['cargo_order', 'transport_order', 'price']

    def __init__(self, *args, **kwargs):
        self.carrier = kwargs.pop('carrier', None)
        super().__init__(*args, **kwargs)
        
        # Ограничиваем выбор только теми заказами, которые доступны
        self.fields['cargo_order'].queryset = CargoOrder.objects.filter(
            contracts__isnull=True
        )
        
        # Ограничиваем выбор транспорта только доступными единицами перевозчика
        self.fields['transport_order'].queryset = TransportOrder.objects.filter(
            carrier=self.carrier,
            contracts__isnull=True
        )
    
    def clean(self):
        cleaned_data = super().clean()
        cargo_order = cleaned_data.get('cargo_order')
        transport_order = cleaned_data.get('transport_order')

        if not cargo_order or not transport_order:
            raise ValidationError("Select both cargo order and transport unit.")

        if transport_order.contracts.exists():
            raise ValidationError("Selected transport unit is already in a contract.")

        if cargo_order.contracts.exists():
            raise ValidationError("Selected cargo order is already in a contract.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Генерируем уникальный номер контракта
        instance.contract_number = f"CONTRACT-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Устанавливаем дедлайны
        instance.payment_deadline = timezone.now() + timezone.timedelta(days=7)
        instance.delivery_deadline = timezone.now() + timezone.timedelta(days=14)
        instance.accepted = True
        
        if commit:
            instance.save()
        return instance
