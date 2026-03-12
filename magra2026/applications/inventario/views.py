from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView, TemplateView, View,
)
from django.http import HttpResponseRedirect, JsonResponse

from .models import (
    Producto, Categoria, UnidadMedida, Proveedor,
    Almacen, Movimiento, AjusteInventario, Alerta,
)
from .forms import (
    ProductoForm, CategoriaForm, UnidadMedidaForm, ProveedorForm,
    AlmacenForm, EntradaStockForm, SalidaStockForm,
    AjusteInventarioForm, FiltroMovimientoForm,
)
from .services import InventarioService, AlertaService

# Importar mixins por sección
from applications.users.mixins import (
    DashboardMixin,
    ProductoMixin,
    StockMixin,
    MovimientoMixin,
    AjusteMixin,
    AlertaMixin,
    AlmacenMixin,
    ProveedorMixin,
    CategoriaMixin,
    UnidadMedidaMixin,
)
from applications.users.models import User


# ══════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════
class DashboardInventarioView(DashboardMixin, TemplateView):
    template_name = 'inventario/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_productos']  = Producto.objects.activos().count()
        ctx['alertas_activas']  = Alerta.objects.count_activas()
        ctx['total_movimientos']= Movimiento.objects.del_mes().count()
        ctx['ajustes_pendientes']= AjusteInventario.objects.filter(estado='P').count()
        ctx['ultimos_movimientos'] = Movimiento.objects.select_related(
            'producto', 'usuario').order_by('-fecha')[:10]
        ctx['alertas_recientes'] = Alerta.objects.activas().order_by('-created')[:5]
        return ctx


# ══════════════════════════════════════════
#  STOCK RESUMEN
# ══════════════════════════════════════════
class StockResumenView(StockMixin, TemplateView):
    template_name = 'inventario/stock/resumen.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['bajo_minimo']            = Producto.objects.con_stock_minimo()
        ctx['sobre_maximo']           = Producto.objects.con_stock_maximo()
        ctx['por_vencer']             = Producto.objects.por_vencer(dias=30)
        ctx['valor_total']            = Producto.objects.activos().aggregate(
            total=Sum('stock_actual'))['total'] or 0
        ctx['total_skus']             = Producto.objects.activos().count()
        ctx['valor_total_inventario'] = ctx['valor_total']
        ctx['productos_bajo_minimo']  = ctx['bajo_minimo']
        ctx['productos_sobre_maximo'] = ctx['sobre_maximo']
        ctx['productos_por_vencer']   = ctx['por_vencer']
        return ctx

# ══════════════════════════════════════════
#  PRODUCTO
# ══════════════════════════════════════════
class ProductoListView(ProductoMixin, ListView):
    template_name = 'inventario/producto/lista.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        qs = Producto.objects.activos().select_related(
            'categoria', 'almacen', 'unidad_medida')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(sku__icontains=q))
        categoria = self.request.GET.get('categoria')
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        almacen = self.request.GET.get('almacen')
        if almacen:
            qs = qs.filter(almacen_id=almacen)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categorias'] = Categoria.objects.filter(activo=True)
        ctx['almacenes']  = Almacen.objects.filter(activo=True)
        return ctx


class ProductoDetailView(ProductoMixin, DetailView):
    model = Producto
    template_name = 'inventario/producto/detalle.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['movimientos'] = Movimiento.objects.por_producto(
            self.object.pk).order_by('-fecha')[:20]
        ctx['form_entrada'] = EntradaStockForm()
        ctx['form_salida']  = SalidaStockForm(producto=self.object)
        return ctx


class ProductoCreateView(ProductoMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto/form.html'
    success_url = reverse_lazy('inventario_app:producto-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado correctamente.')
        return super().form_valid(form)


class ProductoUpdateView(ProductoMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto/form.html'
    success_url = reverse_lazy('inventario_app:producto-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado correctamente.')
        return super().form_valid(form)


# ══════════════════════════════════════════
#  STOCK ENTRADA / SALIDA
# ══════════════════════════════════════════
class EntradaStockView(MovimientoMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        form = EntradaStockForm(request.POST)
        if form.is_valid():
            try:
                InventarioService.registrar_movimiento(
                    producto=producto,
                    tipo=form.cleaned_data['tipo'],
                    cantidad=form.cleaned_data['cantidad'],
                    precio_unitario=form.cleaned_data.get('precio_unitario'),
                    motivo=form.cleaned_data.get('motivo', ''),
                    documento_referencia=form.cleaned_data.get('documento_referencia', ''),
                    usuario=request.user,
                )
                messages.success(request, 'Entrada registrada correctamente.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
        else:
            messages.error(request, 'Datos inválidos en el formulario.')
        return redirect('inventario_app:producto-detalle', pk=pk)


class SalidaStockView(MovimientoMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        form = SalidaStockForm(request.POST, producto=producto)
        if form.is_valid():
            try:
                InventarioService.registrar_movimiento(
                    producto=producto,
                    tipo=form.cleaned_data['tipo'],
                    cantidad=form.cleaned_data['cantidad'],
                    precio_unitario=form.cleaned_data.get('precio_unitario'),
                    motivo=form.cleaned_data.get('motivo', ''),
                    documento_referencia=form.cleaned_data.get('documento_referencia', ''),
                    usuario=request.user,
                )
                messages.success(request, 'Salida registrada correctamente.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
        else:
            messages.error(request, 'Datos inválidos en el formulario.')
        return redirect('inventario_app:producto-detalle', pk=pk)


# ══════════════════════════════════════════
#  MOVIMIENTOS
# ══════════════════════════════════════════
class MovimientoListView(MovimientoMixin, ListView):
    template_name = 'inventario/movimiento/lista.html'
    context_object_name = 'movimientos'
    paginate_by = 25

    def get_queryset(self):
        qs = Movimiento.objects.select_related(
            'producto', 'usuario').order_by('-fecha')
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
        ctx['form_filtro'] = FiltroMovimientoForm(self.request.GET)
        return ctx


class KardexProductoView(MovimientoMixin, DetailView):
    model = Producto
    template_name = 'inventario/movimiento/kardex.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        movimientos = Movimiento.objects.por_producto(
            self.object.pk).order_by('fecha')
        ctx['movimientos'] = movimientos
        ctx['total_entradas'] = sum(
            m.cantidad for m in movimientos
            if m.tipo in Movimiento.TIPOS_ENTRADA)
        ctx['total_salidas'] = sum(
            m.cantidad for m in movimientos
            if m.tipo in Movimiento.TIPOS_SALIDA)
        return ctx


# ══════════════════════════════════════════
#  AJUSTES
# ══════════════════════════════════════════
class AjusteListView(AjusteMixin, ListView):
    template_name = 'inventario/ajuste/lista.html'
    context_object_name = 'ajustes'
    paginate_by = 20
    queryset = AjusteInventario.objects.select_related(
        'producto', 'solicitado_por', 'aprobado_por').order_by('-created')


class AjusteCreateView(AjusteMixin, CreateView):
    model = AjusteInventario
    form_class = AjusteInventarioForm
    template_name = 'inventario/ajuste/form.html'
    success_url = reverse_lazy('inventario_app:ajuste-lista')

    def form_valid(self, form):
        form.instance.solicitado_por = self.request.user
        messages.success(self.request, 'Ajuste solicitado correctamente.')
        return super().form_valid(form)


class AjusteAprobarView(AjusteMixin, View):
    def post(self, request, pk):
        ajuste = get_object_or_404(AjusteInventario, pk=pk)
        try:
            InventarioService.aprobar_ajuste(ajuste, request.user)
            messages.success(request, 'Ajuste aprobado correctamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('inventario_app:ajuste-lista')


class AjusteRechazarView(AjusteMixin, View):
    def post(self, request, pk):
        ajuste = get_object_or_404(AjusteInventario, pk=pk)
        try:
            InventarioService.rechazar_ajuste(ajuste, request.user)
            messages.success(request, 'Ajuste rechazado.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('inventario_app:ajuste-lista')


# ══════════════════════════════════════════
#  ALERTAS
# ══════════════════════════════════════════
class AlertaListView(AlertaMixin, ListView):
    template_name = 'inventario/alerta/lista.html'
    context_object_name = 'alertas'
    paginate_by = 20

    def get_queryset(self):
        qs = Alerta.objects.select_related('producto').order_by(
            'resuelta', '-prioridad', '-created')
        tipo = self.request.GET.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        resuelta = self.request.GET.get('resuelta')
        if resuelta == '0':
            qs = qs.filter(resuelta=False)
        elif resuelta == '1':
            qs = qs.filter(resuelta=True)
        return qs


class AlertaResolverView(AlertaMixin, View):
    def post(self, request, pk):
        alerta = get_object_or_404(Alerta, pk=pk)
        alerta.resuelta = True
        alerta.fecha_resolucion = timezone.now()
        alerta.save()
        messages.success(request, 'Alerta marcada como resuelta.')
        return redirect('inventario_app:alerta-lista')


# ══════════════════════════════════════════
#  ALMACÉN
# ══════════════════════════════════════════
class AlmacenListView(AlmacenMixin, ListView):
    template_name = 'inventario/almacen/lista.html'
    context_object_name = 'almacenes'
    queryset = Almacen.objects.filter(activo=True)


class AlmacenDetailView(AlmacenMixin, DetailView):
    model = Almacen
    template_name = 'inventario/almacen/detalle.html'
    context_object_name = 'almacen'


class AlmacenCreateView(AlmacenMixin, CreateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen/form.html'
    success_url = reverse_lazy('inventario_app:almacen-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Almacén creado correctamente.')
        return super().form_valid(form)


class AlmacenUpdateView(AlmacenMixin, UpdateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen/form.html'
    success_url = reverse_lazy('inventario_app:almacen-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Almacén actualizado.')
        return super().form_valid(form)


# ══════════════════════════════════════════
#  PROVEEDOR
# ══════════════════════════════════════════
class ProveedorListView(ProveedorMixin, ListView):
    template_name = 'inventario/proveedor/lista.html'
    context_object_name = 'proveedores'
    queryset = Proveedor.objects.filter(activo=True)


class ProveedorDetailView(ProveedorMixin, DetailView):
    model = Proveedor
    template_name = 'inventario/proveedor/detalle.html'
    context_object_name = 'proveedor'


class ProveedorCreateView(ProveedorMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'inventario/proveedor/form.html'
    success_url = reverse_lazy('inventario_app:proveedor-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado correctamente.')
        return super().form_valid(form)


class ProveedorUpdateView(ProveedorMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'inventario/proveedor/form.html'
    success_url = reverse_lazy('inventario_app:proveedor-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado.')
        return super().form_valid(form)


# ══════════════════════════════════════════
#  CATEGORÍA
# ══════════════════════════════════════════
class CategoriaListView(CategoriaMixin, ListView):
    template_name = 'inventario/categoria/lista.html'
    context_object_name = 'categorias'
    queryset = Categoria.objects.filter(activo=True)


class CategoriaCreateView(CategoriaMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventario/categoria/form.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada correctamente.')
        return super().form_valid(form)


class CategoriaUpdateView(CategoriaMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventario/categoria/form.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada.')
        return super().form_valid(form)


class CategoriaDeleteView(CategoriaMixin, DeleteView):
    model = Categoria
    template_name = 'inventario/categoria/confirmar_eliminar.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría eliminada.')
        return super().form_valid(form)


# ══════════════════════════════════════════
#  UNIDAD DE MEDIDA
# ══════════════════════════════════════════
class UnidadMedidaListView(UnidadMedidaMixin, ListView):
    template_name = 'inventario/unidad_medida/lista.html'
    context_object_name = 'unidades'
    queryset = UnidadMedida.objects.filter(activo=True)


class UnidadMedidaCreateView(UnidadMedidaMixin, CreateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'inventario/unidad_medida/form.html'
    success_url = reverse_lazy('inventario_app:unidad-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Unidad creada correctamente.')
        return super().form_valid(form)


class UnidadMedidaUpdateView(UnidadMedidaMixin, UpdateView):
    model = UnidadMedida
    form_class = UnidadMedidaForm
    template_name = 'inventario/unidad_medida/form.html'
    success_url = reverse_lazy('inventario_app:unidad-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Unidad actualizada.')
        return super().form_valid(form)


class UnidadMedidaDeleteView(UnidadMedidaMixin, DeleteView):
    model = UnidadMedida
    template_name = 'inventario/unidad_medida/confirmar_eliminar.html'
    success_url = reverse_lazy('inventario_app:unidad-lista')

    def form_valid(self, form):
        messages.success(self.request, 'Unidad eliminada.')
        return super().form_valid(form)