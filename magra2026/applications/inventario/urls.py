from django.urls import path
from . import views

app_name = 'inventario_app'

urlpatterns = [

    # Dashboard
    path('inventario/', views.DashboardInventarioView.as_view(), name='dashboard'),

    # Stock resumen
    path('inventario/stock/', views.StockResumenView.as_view(), name='stock-resumen'),

    # Unidad de Medida
    path('inventario/unidades/', views.UnidadMedidaListView.as_view(), name='unidad-lista'),
    path('inventario/unidades/nueva/', views.UnidadMedidaCreateView.as_view(), name='unidad-crear'),
    path('inventario/unidades/<int:pk>/editar/', views.UnidadMedidaUpdateView.as_view(), name='unidad-editar'),
    path('inventario/unidades/<int:pk>/eliminar/', views.UnidadMedidaDeleteView.as_view(), name='unidad-eliminar'),

    # Categorías
    path('inventario/categorias/', views.CategoriaListView.as_view(), name='categoria-lista'),
    path('inventario/categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria-crear'),
    path('inventario/categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria-editar'),
    path('inventario/categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria-eliminar'),

    # Proveedores
    path('inventario/proveedores/', views.ProveedorListView.as_view(), name='proveedor-lista'),
    path('inventario/proveedores/nuevo/', views.ProveedorCreateView.as_view(), name='proveedor-crear'),
    path('inventario/proveedores/<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='proveedor-editar'),
    path('inventario/proveedores/<int:pk>/', views.ProveedorDetailView.as_view(), name='proveedor-detalle'),

    # Almacenes
    path('inventario/almacenes/', views.AlmacenListView.as_view(), name='almacen-lista'),
    path('inventario/almacenes/nuevo/', views.AlmacenCreateView.as_view(), name='almacen-crear'),
    path('inventario/almacenes/<int:pk>/editar/', views.AlmacenUpdateView.as_view(), name='almacen-editar'),
    path('inventario/almacenes/<int:pk>/', views.AlmacenDetailView.as_view(), name='almacen-detalle'),

    # Productos
    path('inventario/productos/', views.ProductoListView.as_view(), name='producto-lista'),
    path('inventario/productos/nuevo/', views.ProductoCreateView.as_view(), name='producto-crear'),
    path('inventario/productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto-editar'),
    path('inventario/productos/<int:pk>/', views.ProductoDetailView.as_view(), name='producto-detalle'),

    # Stock — entradas y salidas (se procesan desde el detalle del producto)
    path('inventario/productos/<int:pk>/entrada/', views.EntradaStockView.as_view(), name='stock-entrada'),
    path('inventario/productos/<int:pk>/salida/', views.SalidaStockView.as_view(), name='stock-salida'),

    # Movimientos
    path('inventario/movimientos/', views.MovimientoListView.as_view(), name='movimiento-lista'),
    path('inventario/productos/<int:pk>/kardex/', views.KardexProductoView.as_view(), name='kardex'),

    # Ajustes de inventario
    path('inventario/ajustes/', views.AjusteListView.as_view(), name='ajuste-lista'),
    path('inventario/ajustes/nuevo/', views.AjusteCreateView.as_view(), name='ajuste-crear'),
    path('inventario/ajustes/<int:pk>/aprobar/', views.AjusteAprobarView.as_view(), name='ajuste-aprobar'),
    path('inventario/ajustes/<int:pk>/rechazar/', views.AjusteRechazarView.as_view(), name='ajuste-rechazar'),

    # Alertas
    path('inventario/alertas/', views.AlertaListView.as_view(), name='alerta-lista'),
    path('inventario/alertas/<int:pk>/resolver/', views.AlertaResolverView.as_view(), name='alerta-resolver'),
]


from .urls_reportes import reporte_urlpatterns
urlpatterns += reporte_urlpatterns