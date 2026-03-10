from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from .models import User


# ─────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────
def es_admin_o_super(user):
    return user.is_superuser or user.occupation == User.ADMINISTRADOR


# ─────────────────────────────────────────
#  Base
# ─────────────────────────────────────────
class BasePermisoMixin(LoginRequiredMixin):
    login_url = reverse_lazy('users_app:user-login')
    occupations_permitidas = []   # lista de roles permitidos

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        user = request.user

        # Superusuario: acceso total
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Administrador: acceso total excepto register (se maneja en SuperusuarioMixin)
        if user.occupation == User.ADMINISTRADOR:
            return super().dispatch(request, *args, **kwargs)

        # Gerencia: acceso solo lectura (dispatch pasa, las vistas controlan escritura)
        if user.occupation == User.GERENCIA:
            if User.GERENCIA in self.occupations_permitidas:
                return super().dispatch(request, *args, **kwargs)
            return HttpResponseForbidden(self._mensaje_forbidden())

        # Otros roles: verificar lista
        if user.occupation in self.occupations_permitidas:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden(self._mensaje_forbidden())

    def _mensaje_forbidden(self):
        return """
        <div style="font-family:Segoe UI,sans-serif;display:flex;align-items:center;
                    justify-content:center;min-height:100vh;background:#f4f6f9;">
          <div style="background:#fff;border:1px solid #e3e7ef;border-radius:12px;
                      padding:2.5rem 3rem;text-align:center;max-width:400px;">
            <div style="font-size:2.5rem;margin-bottom:1rem;">🔒</div>
            <h4 style="color:#1a1d23;margin-bottom:.5rem;">Acceso restringido</h4>
            <p style="color:#6b7280;font-size:.9rem;margin-bottom:1.5rem;">
              No tienes permiso para acceder a esta sección.
            </p>
            <a href="javascript:history.back()"
               style="background:#4e9fff;color:#fff;border-radius:8px;
                      padding:.6rem 1.5rem;text-decoration:none;font-size:.88rem;">
              Volver
            </a>
          </div>
        </div>
        """


# ─────────────────────────────────────────
#  Solo superusuario (register)
# ─────────────────────────────────────────
class SuperusuarioMixin(LoginRequiredMixin):
    login_url = reverse_lazy('users_app:user-login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            return HttpResponseForbidden(BasePermisoMixin()._mensaje_forbidden())
        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────
#  Gerencia: solo lectura
#  Bloquea POST en vistas de escritura
# ─────────────────────────────────────────
class SoloLecturaMixin:
    """
    Mezclar con BasePermisoMixin.
    Si el usuario es Gerencia bloquea métodos POST/PUT/DELETE.
    """
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response

    def post(self, request, *args, **kwargs):
        if request.user.occupation == User.GERENCIA and not request.user.is_superuser:
            return HttpResponseForbidden(BasePermisoMixin()._mensaje_forbidden())
        return super().post(request, *args, **kwargs)


# ─────────────────────────────────────────
#  Mixins por sección
# ─────────────────────────────────────────

# Dashboard — todos los roles
class DashboardMixin(BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.ALMACEN,
        User.GERENCIA,
    ]

# Productos — Admin, Ventas, Almacén, Gerencia (lectura)
class ProductoMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.ALMACEN,
        User.GERENCIA,
    ]

# Stock / Resumen — todos
class StockMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.ALMACEN,
        User.GERENCIA,
    ]

# Movimientos — Admin, Almacén, Gerencia (lectura)
class MovimientoMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.ALMACEN,
        User.GERENCIA,
    ]

# Ajustes — Admin, Almacén, Gerencia (lectura)
class AjusteMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.ALMACEN,
        User.GERENCIA,
    ]

# Alertas — Admin, Ventas, Almacén, Gerencia (lectura)
class AlertaMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.ALMACEN,
        User.GERENCIA,
    ]

# Almacenes — Admin, Ventas, Gerencia (lectura)
class AlmacenMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.GERENCIA,
    ]

# Proveedores — Admin, Ventas, Gerencia (lectura)
class ProveedorMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.GERENCIA,
    ]

# Categorías — Admin, Ventas, Gerencia (lectura)
class CategoriaMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.GERENCIA,
    ]

# Unidades — Admin, Ventas, Gerencia (lectura)
class UnidadMedidaMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.VENTAS,
        User.GERENCIA,
    ]

# Usuarios lista — Admin, Gerencia (lectura)
class UsuarioListaMixin(SoloLecturaMixin, BasePermisoMixin):
    occupations_permitidas = [
        User.ADMINISTRADOR,
        User.GERENCIA,
    ]

# Register — solo superusuario (usa SuperusuarioMixin directamente)
# Cambiar contraseña — cualquier usuario logueado (usa LoginRequiredMixin)


# ─────────────────────────────────────────
#  Compatibilidad con código anterior
# ─────────────────────────────────────────
class AdministradorPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.ADMINISTRADOR]

class VentasPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.VENTAS]

class AlmacenPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.ALMACEN]

class GerenciaPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.GERENCIA]