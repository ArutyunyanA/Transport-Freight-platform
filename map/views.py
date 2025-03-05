from django.views.generic import TemplateView
from django.shortcuts import render
from django.conf import settings
from .forms import AddressForm
from geodata.models import get_coordinate_async, get_route  # Асинхронные функции

class MainMapView(TemplateView):
    template_name = 'map/main_map.html'

    async def get(self, request, *args, **kwargs):
        form = AddressForm()
        return render(request, self.template_name, {
            'form': form,
            'mapbox_api_key': settings.MAPBOX_API_KEY,
        })

    async def post(self, request, *args, **kwargs):
        form = AddressForm(request.POST)
        if form.is_valid():
            start_address = form.cleaned_data['start_address']
            end_address = form.cleaned_data['end_address']

            # Асинхронно получаем координаты
            start_coord, end_coord = await self.get_coordinates(start_address, end_address)
            route_info = await self.get_route_info(start_coord, end_coord)

            return render(request, self.template_name, {
                'form': form,
                'coordinate_start': start_coord,
                'coordinate_end': end_coord,
                'mapbox_api_key': settings.MAPBOX_API_KEY,
                'route_info': route_info
            })
        return render(request, self.template_name, {'form': form})

    async def get_coordinates(self, start_address, end_address):
        start = await get_coordinate_async(start_address)
        end = await get_coordinate_async(end_address)
        return start, end

    async def get_route_info(self, start_coord, end_coord):
        route_info = await get_route(start_coord, end_coord)
        return route_info










