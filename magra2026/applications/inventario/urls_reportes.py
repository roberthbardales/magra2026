"""
Agrega estas rutas al urlpatterns de applications/inventario/urls.py
"""
from django.urls import path
from . import views_reportes  # o desde views si las pusiste ahí

reporte_urlpatterns = [

    # Stock actual
    path('reportes/stock/pdf/',   views_reportes.StockPDFView.as_view(),   name='reporte-stock-pdf'),
    path('reportes/stock/excel/', views_reportes.StockExcelView.as_view(), name='reporte-stock-excel'),

    # Kardex por producto
    path('reportes/kardex/<int:pk>/pdf/',   views_reportes.KardexPDFView.as_view(),   name='reporte-kardex-pdf'),
    path('reportes/kardex/<int:pk>/excel/', views_reportes.KardexExcelView.as_view(), name='reporte-kardex-excel'),

    # Movimientos
    path('reportes/movimientos/pdf/',   views_reportes.MovimientosPDFView.as_view(),   name='reporte-movimientos-pdf'),
    path('reportes/movimientos/excel/', views_reportes.MovimientosExcelView.as_view(), name='reporte-movimientos-excel'),

    # Alertas
    path('reportes/alertas/pdf/',   views_reportes.AlertasPDFView.as_view(),   name='reporte-alertas-pdf'),
    path('reportes/alertas/excel/', views_reportes.AlertasExcelView.as_view(), name='reporte-alertas-excel'),

    # Ajustes
    path('reportes/ajustes/pdf/',   views_reportes.AjustesPDFView.as_view(),   name='reporte-ajustes-pdf'),
    path('reportes/ajustes/excel/', views_reportes.AjustesExcelView.as_view(), name='reporte-ajustes-excel'),

    # Proveedores
    path('reportes/proveedores/pdf/',   views_reportes.ProveedoresPDFView.as_view(),   name='reporte-proveedores-pdf'),
    path('reportes/proveedores/excel/', views_reportes.ProveedoresExcelView.as_view(), name='reporte-proveedores-excel'),
]