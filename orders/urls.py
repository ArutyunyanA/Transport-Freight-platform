from django.urls import path
from .views import VirtualWarehouse, update_warehouse_stock
from .views import (
    CargoOrderCreateView, CargoOrderListView,
    TransportOrderCreateView, TransportOrderListView,
    TransportItemCreateView, CargoItemCreateView, 
    CargoOrderDetailView, TransportOrderDetailView, 
    create_contract,
)


app_name = 'orders'

urlpatterns = [
    path('cargo/create/', CargoOrderCreateView.as_view(), name='cargo_order_create'),
    path('cargo/', CargoOrderListView.as_view(), name='cargo_order_list'),
    path('transport/create/', TransportOrderCreateView.as_view(), name='transport_order_create'),
    path('transport/', TransportOrderListView.as_view(), name='transport_order_list'),
    path('cargo-item/create/', CargoItemCreateView.as_view(), name='cargo_item_create'),
    path('transport-item/create/', TransportItemCreateView.as_view(), name='transport_item_create'),
    path('cargo-order/<int:pk>/', CargoOrderDetailView.as_view(), name='cargo_order_detail'),
    path('transport/<int:pk>/', TransportOrderDetailView.as_view(), name='transport_order_detail'),
    path('create-contract/', create_contract, name='create_contract'),
    path('warehouse/', VirtualWarehouse, name='virtual_warehouse'),
    path('warehouse/update/', update_warehouse_stock, name='update_warehouse_stock'),
]

