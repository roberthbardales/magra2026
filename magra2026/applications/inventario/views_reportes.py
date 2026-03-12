"""
Agrega estas vistas al final de applications/inventario/views.py
o en un archivo separado applications/inventario/views_reportes.py
"""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from .models import Producto, Movimiento, AjusteInventario, Alerta, Proveedor
from .reports import (
    reporte_stock_pdf,    reporte_stock_excel,
    reporte_kardex_pdf,   reporte_kardex_excel,
    reporte_movimientos_pdf, reporte_movimientos_excel,
    reporte_alertas_pdf,  reporte_alertas_excel,
    reporte_ajustes_pdf,  reporte_ajustes_excel,
    reporte_proveedores_pdf, reporte_proveedores_excel,
)
from applications.users.mixins import (
    StockMixin, MovimientoMixin, AlertaMixin,
    AjusteMixin, ProveedorMixin,
)


# ── helpers ──────────────────────────────
def _pdf_response(buffer, nombre):
    ts = timezone.now().strftime('%Y%m%d_%H%M')
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}_{ts}.pdf"'
    return response

def _excel_response(buffer, nombre):
    ts = timezone.now().strftime('%Y%m%d_%H%M')
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre}_{ts}.xlsx"'
    return response


# ══════════════════════════════════════════
#  1. STOCK ACTUAL
# ══════════════════════════════════════════
class StockPDFView(StockMixin, View):
    def get(self, request):
        productos = Producto.objects.activos().select_related(
            'categoria', 'almacen', 'unidad_medida').order_by('categoria__nombre', 'nombre')
        buffer = reporte_stock_pdf(productos)
        return _pdf_response(buffer, 'stock_actual')

class StockExcelView(StockMixin, View):
    def get(self, request):
        productos = Producto.objects.activos().select_related(
            'categoria', 'almacen', 'unidad_medida').order_by('categoria__nombre', 'nombre')
        buffer = reporte_stock_excel(productos)
        return _excel_response(buffer, 'stock_actual')


# ══════════════════════════════════════════
#  2. KARDEX POR PRODUCTO
# ══════════════════════════════════════════
class KardexPDFView(MovimientoMixin, View):
    def get(self, request, pk):
        producto    = get_object_or_404(Producto, pk=pk)
        movimientos = Movimiento.objects.por_producto(pk).order_by('fecha')
        buffer = reporte_kardex_pdf(producto, movimientos)
        return _pdf_response(buffer, f'kardex_{producto.sku}')

class KardexExcelView(MovimientoMixin, View):
    def get(self, request, pk):
        producto    = get_object_or_404(Producto, pk=pk)
        movimientos = Movimiento.objects.por_producto(pk).order_by('fecha')
        buffer = reporte_kardex_excel(producto, movimientos)
        return _excel_response(buffer, f'kardex_{producto.sku}')


# ══════════════════════════════════════════
#  3. MOVIMIENTOS POR FECHA
# ══════════════════════════════════════════
class MovimientosPDFView(MovimientoMixin, View):
    def get(self, request):
        qs = Movimiento.objects.select_related(
            'producto', 'usuario').order_by('-fecha')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin    = request.GET.get('fecha_fin')
        if fecha_inicio:
            qs = qs.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha__date__lte=fecha_fin)
        buffer = reporte_movimientos_pdf(qs, fecha_inicio, fecha_fin)
        return _pdf_response(buffer, 'movimientos')

class MovimientosExcelView(MovimientoMixin, View):
    def get(self, request):
        qs = Movimiento.objects.select_related(
            'producto', 'usuario').order_by('-fecha')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin    = request.GET.get('fecha_fin')
        if fecha_inicio:
            qs = qs.filter(fecha__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha__date__lte=fecha_fin)
        buffer = reporte_movimientos_excel(qs, fecha_inicio, fecha_fin)
        return _excel_response(buffer, 'movimientos')


# ══════════════════════════════════════════
#  4. ALERTAS
# ══════════════════════════════════════════
class AlertasPDFView(AlertaMixin, View):
    def get(self, request):
        alertas = Alerta.objects.select_related('producto').order_by('resuelta', '-prioridad')
        buffer = reporte_alertas_pdf(alertas)
        return _pdf_response(buffer, 'alertas')

class AlertasExcelView(AlertaMixin, View):
    def get(self, request):
        alertas = Alerta.objects.select_related('producto').order_by('resuelta', '-prioridad')
        buffer = reporte_alertas_excel(alertas)
        return _excel_response(buffer, 'alertas')


# ══════════════════════════════════════════
#  5. AJUSTES
# ══════════════════════════════════════════
class AjustesPDFView(AjusteMixin, View):
    def get(self, request):
        ajustes = AjusteInventario.objects.select_related(
            'producto', 'solicitado_por', 'aprobado_por').order_by('-created')
        buffer = reporte_ajustes_pdf(ajustes)
        return _pdf_response(buffer, 'ajustes_inventario')

class AjustesExcelView(AjusteMixin, View):
    def get(self, request):
        ajustes = AjusteInventario.objects.select_related(
            'producto', 'solicitado_por', 'aprobado_por').order_by('-created')
        buffer = reporte_ajustes_excel(ajustes)
        return _excel_response(buffer, 'ajustes_inventario')


# ══════════════════════════════════════════
#  6. PROVEEDORES
# ══════════════════════════════════════════
class ProveedoresPDFView(ProveedorMixin, View):
    def get(self, request):
        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
        buffer = reporte_proveedores_pdf(proveedores)
        return _pdf_response(buffer, 'proveedores')

class ProveedoresExcelView(ProveedorMixin, View):
    def get(self, request):
        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
        buffer = reporte_proveedores_excel(proveedores)
        return _excel_response(buffer, 'proveedores')