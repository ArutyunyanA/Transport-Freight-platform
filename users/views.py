from django.urls import reverse_lazy, reverse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, TemplateView
from django.shortcuts import render, redirect
from orders.models import TransportOrder, CargoOrder, ShipmentContract
from .forms import CustomUserRegistrationForm
from .models import CustomUser

class UserRegistrationView(CreateView):
    model = CustomUser
    form_class = CustomUserRegistrationForm
    template_name = "users/registration.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        # Создаем пользователя с помощью стандартного метода
        response = super().form_valid(form)
        user = self.object  # Новый пользователь

        # Создаем профиль в зависимости от типа пользователя, если его еще нет
        if user.user_type == 'shipper':
            from .models import ShipperProfile
            ShipperProfile.objects.get_or_create(user=user)
        elif user.user_type == 'carrier':
            from .models import CarrierProfile
            CarrierProfile.objects.get_or_create(user=user)
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class DashboardRedirectView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == 'shipper':
                return redirect('users:shipper_dashboard')
            elif request.user.user_type == 'carrier':
                return redirect('users:carrier_dashboard')
        return redirect('users:login')


class ShipperDashboardView(TemplateView):
    template_name = "users/shipper_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Используем имя обратной связи, как определено в модели: related_name="shipper"
        try:
            shipper_profile = self.request.user.shipper
        except Exception:
            shipper_profile = None
        context['profile'] = shipper_profile
        if shipper_profile:
            context['recent_orders'] = CargoOrder.objects.filter(shipper=shipper_profile).order_by("-created_at")[:10]
            context['total_orders'] = CargoOrder.objects.filter(shipper=shipper_profile).count()
        else:
            context['recent_orders'] = []
            context['total_orders'] = 0
        return context


class CarrierDashboardView(TemplateView):
    template_name = "users/carrier_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Используем имя обратной связи, как определено в модели: related_name="carrier"
        try:
            carrier_profile = self.request.user.carrier
        except Exception:
            carrier_profile = None
        context['profile'] = carrier_profile
        if carrier_profile:
            context['recent_transport_orders'] = TransportOrder.objects.filter(carrier=carrier_profile).order_by("-created_at")[:10]
            context['total_transport_orders'] = TransportOrder.objects.filter(carrier=carrier_profile).count()
        else:
            context['recent_transport_orders'] = []
            context['total_transport_orders'] = 0
        return context



