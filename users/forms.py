from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(required=True)
    address = forms.CharField(required=True)
    vat_number = forms.CharField(required=True)
    phone_number = forms.CharField(required=False)
    contact_person = forms.CharField(required=True)
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPES, required=True)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "company_name",
            "address",
            "vat_number",
            "phone_number",
            "contact_person",
            "user_type",
            "password1",
            "password2",
        )


