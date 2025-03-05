from django.http import JsonResponse
from django.views import View

class MapboxAutocompleteView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Mapbox autocomplete works!"})

