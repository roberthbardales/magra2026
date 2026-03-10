from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from django.utils import timezone

from applications.users.mixins import (
    AdministradorPermisoMixin,
    AlmacenPermisoMixin,
    VentasPermisoMixin,
    GerenciaPermisoMixin,
    BasePermisoMixin,
)
from .models import (
    UnidadMedida, Categoria, Proveedor, Almacen,
    Producto, Movimiento, AjusteInventario, Alerta
)
from .forms import (
    UnidadMedidaForm, CategoriaForm, ProveedorForm, AlmacenForm,
    ProductoForm, EntradaStockForm, SalidaStockForm,
    AjusteInventarioForm, FiltroMovimientoForm
)
from .services import InventarioService, AlertaService


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
class DashboardInventarioView(BasePermisoMixin, TemplateView):
    template_name = 'inventario/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_productos'] = Producto.objects.activos().count()
        ctx['alertas_activas'] = Alerta.objects.activas().count()
        ctx['alertas_altas'] = Alerta.objects.altas().count()
        ctx['stock_minimo'] = Producto.objects.con_stock_minimo().count()
        ctx['movimientos_hoy'] = Movimiento.objects.filter(
            fecha__date=timezone.now().date()
        ).count()
        ctx['ultimos_movimientos'] = Movimiento.objects.select_related(
            'producto', 'usuario'
        )[:10]
        ctx['alertas_recientes'] = Alerta.objects.activas().select_related(
            'producto'
        )[:5]
        return ctx


# ─────────────────────────────────────────────
#  UNIDAD DE MEDIDA
# ─────────────────────────────────────────────
class UnidadMedidaListView(AdministradorPermisoMixin, ListView):
    model = UnidadMedida
    template_name = 'inventario/unidad_medida/lista.html'
    context_object_name = 'unidades'
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = UnidadMedida.objects.all()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(abreviatura__icontains=q))
        return qs


class UnidadMedidaCreateView(AdministradorPermisoMixin, CreateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'inventario/unidad_medida/form.html'
    success_url = reverse_lazy('inventario_app:unidad-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Unidad de medida creada correctamente.')
        return super().form_valid(form)


class UnidadMedidaUpdateView(AdministradorPermisoMixin, UpdateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'inventario/unidad_medida/form.html'
    success_url = reverse_lazy('inventario_app:unidad-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Unidad de medida actualizada.')
        return super().form_valid(form)


class UnidadMedidaDeleteView(AdministradorPermisoMixin, DeleteView):
    model = UnidadMedida
    template_name = 'inventario/unidad_medida/confirmar_eliminar.html'
    success_url = reverse_lazy('inventario_app:unidad-lista')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Unidad de medida eliminada.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────
#  CATEGORÍA
# ─────────────────────────────────────────────
class CategoriaListView(AdministradorPermisoMixin, ListView):
    model = Categoria
    template_name = 'inventario/categoria/lista.html'
    context_object_name = 'categorias'
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = Categoria.objects.all()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs


class CategoriaCreateView(AdministradorPermisoMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventario/categoria/form.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada correctamente.')
        return super().form_valid(form)


class CategoriaUpdateView(AdministradorPermisoMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventario/categoria/form.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada.')
        return super().form_valid(form)


class CategoriaDeleteView(AdministradorPermisoMixin, DeleteView):
    model = Categoria
    template_name = 'inventario/categoria/confirmar_eliminar.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Categoría eliminada.')
        return super().delete(request, *args, **kwargs)


# ─────────────────────────────────────────────
#  PROVEEDOR
# ─────────────────────────────────────────────
class ProveedorListView(AdministradorPermisoMixin, ListView):
    model = Proveedor
    template_name = 'inventario/proveedor/lista.html'
    context_object_name = 'proveedores'
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = Proveedor.objects.all()
        if q:
            qs = qs.filter(
                Q(razon_social__icontains=q) |
                Q(ruc__icontains=q) |
                Q(contacto__icontains=q)
            )
        return qs


class ProveedorCreateView(AdministradorPermisoMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'inventario/proveedor/form.html'
    success_url = reverse_lazy('inventario_app:proveedor-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado correctamente.')
        return super().form_valid(form)


class ProveedorUpdateView(AdministradorPermisoMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'inventario/proveedor/form.html'
    success_url = reverse_lazy('inventario_app:proveedor-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado.')
        return super().form_valid(form)


class ProveedorDetailView(BasePermisoMixin, DetailView):
    model = Proveedor
    template_name = 'inventario/proveedor/detalle.html'
    context_object_name = 'proveedor'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['productos'] = self.object.productos.filter(estado='A')
        return ctx


# ─────────────────────────────────────────────
#  ALMACÉN
# ─────────────────────────────────────────────
class AlmacenListView(AdministradorPermisoMixin, ListView):
    model = Almacen
    template_name = 'inventario/almacen/lista.html'
    context_object_name = 'almacenes'

    def get_queryset(self):
        return Almacen.objects.select_related('responsable').all()


class AlmacenCreateView(AdministradorPermisoMixin, CreateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen/form.html'
    success_url = reverse_lazy('inventario_app:almacen-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Almacén creado correctamente.')
        return super().form_valid(form)


class AlmacenUpdateView(AdministradorPermisoMixin, UpdateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen/form.html'
    success_url = reverse_lazy('inventario_app:almacen-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Almacén actualizado.')
        return super().form_valid(form)


class AlmacenDetailView(BasePermisoMixin, DetailView):
    model = Almacen
    template_name = 'inventario/almacen/detalle.html'
    context_object_name = 'almacen'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['productos'] = self.object.productos.filter(estado='A').select_related(
            'categoria', 'unidad_medida'
        )
        ctx['total_productos'] = ctx['productos'].count()
        ctx['valor_total'] = ctx['productos'].aggregate(
            total=Sum(F('stock_actual') * F('precio_compra'))
        )['total'] or 0
        return ctx


# ─────────────────────────────────────────────
#  PRODUCTO
# ─────────────────────────────────────────────
class ProductoListView(BasePermisoMixin, ListView):
    model = Producto
    template_name = 'inventario/producto/lista.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        categoria = self.request.GET.get('categoria', '')
        almacen = self.request.GET.get('almacen', '')
        estado = self.request.GET.get('estado', '')

        qs = Producto.objects.select_related(
            'categoria', 'unidad_medida', 'proveedor', 'almacen'
        ).all()

        if q:
            qs = qs.filter(Q(sku__icontains=q) | Q(nombre__icontains=q))
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        if almacen:
            qs = qs.filter(almacen_id=almacen)
        if estado:
            qs = qs.filter(estado=estado)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categorias'] = Categoria.objects.filter(activo=True)
        ctx['almacenes'] = Almacen.objects.filter(activo=True)
        return ctx


class ProductoCreateView(AdministradorPermisoMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto/form.html'
    success_url = reverse_lazy('inventario_app:producto-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)


class ProductoUpdateView(AdministradorPermisoMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto/form.html'
    success_url = reverse_lazy('inventario_app:producto-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado.')
        return super().form_valid(form)


class ProductoDetailView(BasePermisoMixin, DetailView):
    model = Producto
    template_name = 'inventario/producto/detalle.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['ultimos_movimientos'] = self.object.movimientos.select_related(
            'usuario'
        )[:20]
        ctx['alertas_activas'] = self.object.alertas.filter(resuelta=False)
        ctx['entrada_form'] = EntradaStockForm()
        ctx['salida_form'] = SalidaStockForm(producto=self.object)
        return ctx


# ─────────────────────────────────────────────
#  STOCK — ENTRADAS Y SALIDAS
# ─────────────────────────────────────────────
class EntradaStockView(AlmacenPermisoMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        form = EntradaStockForm(request.POST)
        if form.is_valid():
            try:
                InventarioService.registrar_movimiento(
                    producto=producto,
                    tipo=form.cleaned_data['tipo'],
                    cantidad=form.cleaned_data['cantidad'],
                    usuario=request.user,
                    precio_unitario=form.cleaned_data['precio_unitario'],
                    motivo=form.cleaned_data.get('motivo', ''),
                    documento=form.cleaned_data.get('documento_referencia', ''),
                )
                messages.success(request, 'Entrada registrada correctamente.')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Datos inválidos en el formulario.')
        return redirect('inventario_app:producto-detalle', pk=pk)


class SalidaStockView(AlmacenPermisoMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        form = SalidaStockForm(producto=producto, data=request.POST)
        if form.is_valid():
            try:
                InventarioService.registrar_movimiento(
                    producto=producto,
                    tipo=form.cleaned_data['tipo'],
                    cantidad=form.cleaned_data['cantidad'],
                    usuario=request.user,
                    precio_unitario=form.cleaned_data['precio_unitario'],
                    motivo=form.cleaned_data.get('motivo', ''),
                    documento=form.cleaned_data.get('documento_referencia', ''),
                )
                messages.success(request, 'Salida registrada correctamente.')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Datos inválidos en el formulario.')
        return redirect('inventario_app:producto-detalle', pk=pk)


# ─────────────────────────────────────────────
#  MOVIMIENTOS / KARDEX
# ─────────────────────────────────────────────
class MovimientoListView(BasePermisoMixin, ListView):
    model = Movimiento
    template_name = 'inventario/movimiento/lista.html'
    context_object_name = 'movimientos'
    paginate_by = 25

    def get_queryset(self):
        qs = Movimiento.objects.select_related('producto', 'usuario').all()
        form = FiltroMovimientoForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('producto'):
                qs = qs.filter(producto=form.cleaned_data['producto'])
            if form.cleaned_data.get('tipo'):
                qs = qs.filter(tipo=form.cleaned_data['tipo'])
            if form.cleaned_data.get('fecha_inicio'):
                qs = qs.filter(fecha__date__gte=form.cleaned_data['fecha_inicio'])
            if form.cleaned_data.get('fecha_fin'):
                qs = qs.filter(fecha__date__lte=form.cleaned_data['fecha_fin'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro_form'] = FiltroMovimientoForm(self.request.GET)
        return ctx


class KardexProductoView(BasePermisoMixin, ListView):
    """Kardex individual de un producto."""
    template_name = 'inventario/movimiento/kardex.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_queryset(self):
        self.producto = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return Movimiento.objects.filter(
            producto=self.producto
        ).select_related('usuario').order_by('-fecha')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['producto'] = self.producto
        ctx['total_entradas'] = Movimiento.objects.entradas().filter(
            producto=self.producto
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        ctx['total_salidas'] = Movimiento.objects.salidas().filter(
            producto=self.producto
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        return ctx


# ─────────────────────────────────────────────
#  AJUSTE DE INVENTARIO
# ─────────────────────────────────────────────
class AjusteListView(AdministradorPermisoMixin, ListView):
    model = AjusteInventario
    template_name = 'inventario/ajuste/lista.html'
    context_object_name = 'ajustes'
    paginate_by = 20

    def get_queryset(self):
        return AjusteInventario.objects.select_related(
            'producto', 'solicitado_por', 'aprobado_por'
        ).all()


class AjusteCreateView(AlmacenPermisoMixin, CreateView):
    model = AjusteInventario
    form_class = AjusteInventarioForm
    template_name = 'inventario/ajuste/form.html'
    success_url = reverse_lazy('inventario_app:ajuste-lista')

    def form_valid(self, form):
        ajuste = form.save(commit=False)
        ajuste.cantidad_sistema = ajuste.producto.stock_actual
        ajuste.solicitado_por = self.request.user
        ajuste.save()
        messages.success(self.request, 'Ajuste solicitado. Pendiente de aprobación.')
        return redirect(self.success_url)


class AjusteAprobarView(AdministradorPermisoMixin, View):
    def post(self, request, pk):
        ajuste = get_object_or_404(AjusteInventario, pk=pk)
        try:
            InventarioService.aprobar_ajuste(ajuste, request.user)
            messages.success(request, 'Ajuste aprobado y stock actualizado.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('inventario_app:ajuste-lista')


class AjusteRechazarView(AdministradorPermisoMixin, View):
    def post(self, request, pk):
        ajuste = get_object_or_404(AjusteInventario, pk=pk)
        try:
            InventarioService.rechazar_ajuste(ajuste, request.user)
            messages.success(request, 'Ajuste rechazado.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('inventario_app:ajuste-lista')


# ─────────────────────────────────────────────
#  ALERTAS
# ─────────────────────────────────────────────
class AlertaListView(BasePermisoMixin, ListView):
    model = Alerta
    template_name = 'inventario/alerta/lista.html'
    context_object_name = 'alertas'
    paginate_by = 25

    def get_queryset(self):
        tipo = self.request.GET.get('tipo', '')
        prioridad = self.request.GET.get('prioridad', '')
        resuelta = self.request.GET.get('resuelta', '0')

        qs = Alerta.objects.select_related('producto').all()

        if resuelta == '0':
            qs = qs.filter(resuelta=False)
        elif resuelta == '1':
            qs = qs.filter(resuelta=True)

        if tipo:
            qs = qs.filter(tipo=tipo)
        if prioridad:
            qs = qs.filter(prioridad=prioridad)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipos'] = Alerta.TIPO_CHOICES
        ctx['prioridades'] = Alerta.PRIORIDAD_CHOICES
        return ctx


class AlertaResolverView(BasePermisoMixin, View):
    def post(self, request, pk):
        alerta = get_object_or_404(Alerta, pk=pk)
        alerta.resuelta = True
        alerta.fecha_resolucion = timezone.now()
        alerta.save()
        messages.success(request, 'Alerta marcada como resuelta.')
        return redirect('inventario_app:alerta-lista')


# ─────────────────────────────────────────────
#  STOCK — Vista resumen
# ─────────────────────────────────────────────
class StockResumenView(BasePermisoMixin, TemplateView):
    template_name = 'inventario/stock/resumen.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['productos_bajo_minimo'] = Producto.objects.con_stock_minimo().select_related(
            'categoria', 'almacen'
        )
        ctx['productos_sobre_maximo'] = Producto.objects.con_stock_maximo().select_related(
            'categoria', 'almacen'
        )
        ctx['productos_por_vencer'] = Producto.objects.por_vencer().select_related(
            'categoria', 'almacen'
        )
        ctx['valor_total_inventario'] = Producto.objects.activos().aggregate(
            total=Sum(F('stock_actual') * F('precio_compra'))
        )['total'] or 0
        ctx['total_skus'] = Producto.objects.activos().count()
        return ctx