from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from .models import User


def check_occupation_user(required_occupation, user_occupation):
    return user_occupation == User.ADMINISTRADOR or user_occupation == required_occupation


class BasePermisoMixin(LoginRequiredMixin):
    login_url = reverse_lazy('users_app:user-login')
    occupation_requerida = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not check_occupation_user(self.occupation_requerida, request.user.occupation):  # ← corregido
            return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")

        return super().dispatch(request, *args, **kwargs)


class AdministradorPermisoMixin(BasePermisoMixin):
    occupation_requerida = User.ADMINISTRADOR


class VentasPermisoMixin(BasePermisoMixin):
    occupation_requerida = User.VENTAS


class AlmacenPermisoMixin(BasePermisoMixin):
    occupation_requerida = User.ALMACEN


class GerenciaPermisoMixin(BasePermisoMixin):
    occupation_requerida = User.GERENCIA