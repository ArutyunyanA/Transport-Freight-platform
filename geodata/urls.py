from django.urls import path
from . import views

app_name = 'geodata'

urlpatterns = [
    path('autocomplete/', views.MapboxAutocompleteView.as_view(), name='autocomplete'),
]