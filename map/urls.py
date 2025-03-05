from django.urls import path
from .views import MainMapView
from orders.views import ShowOrderRouteView

app_name = 'map'

urlpatterns = [
    path('main/', MainMapView.as_view(), name='main_map'),
    path('order/<int:order_id>/', ShowOrderRouteView.as_view(), name='show_order_route'),
]