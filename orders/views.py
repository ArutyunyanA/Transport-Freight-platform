import asyncio
import json
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import (
    CargoOrder, TransportOrder, VirtualWarehouse, 
    CargoItem, TransportItem, ShipmentContract, 
    TransportCategory,
    )
from asgiref.sync import async_to_sync
from django.utils.safestring import mark_safe
from .forms import CargoOrderForm, TransportOrderForm, CargoItemForm, TransportItemForm, ShipmentContractForm
from geodata.models import get_coordinate_async, get_route


# Создание грузового заказа
class CargoOrderCreateView(CreateView):
    model = CargoOrder
    form_class = CargoOrderForm
    template_name = 'orders/cargo_order_form.html'
    success_url = reverse_lazy('orders:cargo_order_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


    def form_valid(self, form):
        loading_address = form.cleaned_data.get('loading_address')
        unloading_address = form.cleaned_data.get('unloading_address')

        # Асинхронная обработка в синхронном методе
        async def process_coordinates():
            # Асинхронно получаем координаты
            loading_coords, unloading_coords = await asyncio.gather(
                get_coordinate_async(loading_address),
                get_coordinate_async(unloading_address)
            )
            return loading_coords, unloading_coords

        # Запуск асинхронной функции в синхронном контексте
        loading_coords, unloading_coords = asyncio.run(process_coordinates())

        # Проверяем корректность координат
        if not loading_coords:
            form.add_error('loading_address', 'Не удалось получить координаты для адреса погрузки.')
            return self.form_invalid(form)
        if not unloading_coords:
            form.add_error('unloading_address', 'Не удалось получить координаты для адреса выгрузки.')
            return self.form_invalid(form)

        # Конвертируем в JSON
        form.instance.loading_points = [
            {"city": loading_address, "coordinates": loading_coords}
        ]
        form.instance.unloading_points = [
            {"city": unloading_address, "coordinates": unloading_coords}
        ]

        # Получаем маршрут
        route_info = asyncio.run(get_route(loading_coords, unloading_coords))
        form.instance.route_info = route_info

        form.instance.shipper = self.request.user.shipper

        form.save()
        return HttpResponseRedirect(self.success_url)



# Список грузовых заказов с пагинацией
class CargoOrderListView(ListView):
    model = CargoOrder
    template_name = 'orders/cargo_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(cargo_item__name__icontains=q)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__id=category)
        return queryset.order_by('-created_at')

class CargoOrderDetailView(DetailView):
    model = CargoOrder
    template_name = 'orders/cargo_order_detail.html'
    context_object_name = 'order'

# Создание транспортного заказа
class TransportOrderCreateView(CreateView):
    model = TransportOrder
    form_class = TransportOrderForm
    template_name = 'orders/transport_order_form.html'
    success_url = reverse_lazy('orders:transport_order_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


    def form_valid(self, form):
        loading_address = form.cleaned_data.get('loading_address')
        unloading_address = form.cleaned_data.get('unloading_address')

        # Асинхронная обработка в синхронном методе
        async def process_coordinates():
            # Асинхронно получаем координаты
            loading_coords, unloading_coords = await asyncio.gather(
                get_coordinate_async(loading_address),
                get_coordinate_async(unloading_address)
            )
            return loading_coords, unloading_coords

        # Запуск асинхронной функции в синхронном контексте
        loading_coords, unloading_coords = asyncio.run(process_coordinates())

        # Проверяем корректность координат
        if not loading_coords:
            form.add_error('loading_address', 'Не удалось получить координаты для адреса погрузки.')
            return self.form_invalid(form)
        if not unloading_coords:
            form.add_error('unloading_address', 'Не удалось получить координаты для адреса выгрузки.')
            return self.form_invalid(form)

        # Конвертируем в JSON
        form.instance.loading_points = [
            {"city": loading_address, "coordinates": loading_coords}
        ]
        form.instance.unloading_points = [
            {"city": unloading_address, "coordinates": unloading_coords}
        ]

        # Получаем маршрут
        route_info = asyncio.run(get_route(loading_coords, unloading_coords))
        form.instance.route_info = route_info

        form.instance.carrier = self.request.user.carrier

        form.save()
        return HttpResponseRedirect(self.success_url)

# Список транспортных заказов с пагинацией
class TransportOrderListView(ListView):
    model = TransportOrder
    template_name = 'orders/transport_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(transport_items__trailer_number__icontains=q)
        transport_type = self.request.GET.get('transport_type')
        if transport_type:
            queryset = queryset.filter(transport_items__trailer_type=transport_type)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем список категорий для формы поиска, если нужно:
        context['transport_categories'] = TransportCategory.objects.all()
        return context


class TransportOrderDetailView(DetailView):
    model = TransportOrder
    template_name = 'orders/transport_order_detail.html'
    context_object_name = 'order'


@login_required
def create_contract(request):
    carrier = request.user.carrier # Убеждаемся, что пользователь — перевозчик

    if request.method == "POST":
        form = ShipmentContractForm(request.POST, carrier=carrier)
        if form.is_valid():
            form.save()
            messages.success(request, "Contract successfully created!")
            return redirect('orders:order_list')
        else:
            messages.error(request, "Contract creation failed. Please check the form.")
    else:
        form = ShipmentContractForm(carrier=carrier)

    return render(request, 'orders/create_contract.html', {'form': form})


class ShowOrderRouteView(TemplateView):
    template_name = 'map/show_order_route.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        try:
            order = CargoOrder.objects.get(pk=order_id)
        except CargoOrder.DoesNotExist:
            raise Http404("Order not found")

        # Если маршрут уже сохранён, используем его; иначе пустой список
        route_info = order.route_info if order.route_info else []
        first_route = route_info[0] if route_info else {}
        distance = first_route.get('distance', 0)
        geometry = first_route.get('geometry', {})

        # Расчёты: время в пути и стоимость топлива
        travel_time = (distance / 85) * 60  # минут
        fuel_cost = (distance * 0.3) * 1.6   # евро

        context.update({
            'loading_points': order.loading_points or [],
            'unloading_points': order.unloading_points or [],
            'route_info': route_info,
            'route_geometry': mark_safe(json.dumps(geometry)),
            'mapbox_api_key': getattr(settings, 'MAPBOX_API_KEY', ''),
            'travel_time': round(travel_time, 2),
            'fuel_cost': round(fuel_cost, 2),
            'order_id': order.pk,  # чтобы шаблон мог отобразить номер заказа
        })
        return context





@method_decorator(login_required, name='dispatch')
class CargoItemCreateView(CreateView):
    model = CargoItem
    form_class = CargoItemForm
    template_name = "orders/cargo_item_form.html"
    success_url = reverse_lazy("orders:cargo_order_list")

    def form_valid(self, form):
        form.instance.shipper = self.request.user.shipper
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class TransportItemCreateView(CreateView):
    model = TransportItem
    form_class = TransportItemForm
    template_name = "orders/transport_item_form.html"
    success_url = reverse_lazy("orders:transport_order_list")

    def form_valid(self, form):
        form.instance.carrier = self.request.user.carrier
        return super().form_valid(form)

# Функциональное представление для обновления склада (если требуется, можно оставить стандартным)
@login_required
def update_warehouse_stock(request):
    warehouse = get_object_or_404(VirtualWarehouse, shipper=request.user.shipper)
    warehouse.update_stock()
    stocks = warehouse.warehousestock_set.select_related('item').all()
    return render(request, 'orders/virtual_warehouse.html', {'warehouse': warehouse, 'stocks': stocks})
