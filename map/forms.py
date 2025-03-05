from django import forms

class AddressForm(forms.Form):
    start_address = forms.CharField(label='Адрес погрузки', max_length=255)
    end_address = forms.CharField(label='Адрес выгрузки', max_length=255)