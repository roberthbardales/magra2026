from django.db import models
from django.conf import settings
from django.utils import timezone
from model_utils.models import TimeStampedModel
from .managers import ProductoManager, MovimientoManager, AlertaManager



class UnidadMedida(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=50, unique=True)
    abreviatura = models.CharField('Abreviatura', max_length=10, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.abreviatura})'


class Categoria(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(TimeStampedModel):
    razon_social = models.CharField('Razón Social', max_length=200)
    ruc = models.CharField('RUC', max_length=20, unique=True)
    contacto = models.CharField('Contacto', max_length=100, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    direccion = models.TextField('Dirección', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']

    def __str__(self):
        return f'{self.razon_social} ({self.ruc})'


class Almacen(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='almacenes',
        verbose_name='Responsable'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(TimeStampedModel):
    # Estado del producto
    ACTIVO = 'A'
    INACTIVO = 'I'
    DESCONTINUADO = 'D'
    ESTADO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
        (DESCONTINUADO, 'Descontinuado'),
    )

    sku = models.CharField('SKU', max_length=50, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT,
        related_name='productos', verbose_name='Categoría'
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida, on_delete=models.PROTECT,
        related_name='productos', verbose_name='Unidad de Medida'
    )
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='productos', verbose_name='Proveedor'
    )
    almacen = models.ForeignKey(
        Almacen, on_delete=models.PROTECT,
        related_name='productos', verbose_name='Almacén'
    )
    precio_compra = models.DecimalField('Precio Compra', max_digits=12, decimal_places=2, default=0)
    precio_venta = models.DecimalField('Precio Venta', max_digits=12, decimal_places=2, default=0)
    stock_actual = models.IntegerField('Stock Actual', default=0)
    stock_minimo = models.IntegerField('Stock Mínimo', default=5)
    stock_maximo = models.IntegerField('Stock Máximo', default=100)
    fecha_vencimiento = models.DateField('Fecha Vencimiento', null=True, blank=True)
    imagen = models.ImageField('Imagen', upload_to='productos/', null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default=ACTIVO)

    objects = ProductoManager()

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.sku} - {self.nombre}'

    @property
    def tiene_alerta_minimo(self):
        return self.stock_actual <= self.stock_minimo

    @property
    def tiene_alerta_maximo(self):
        return self.stock_actual >= self.stock_maximo

    @property
    def tiene_alerta_vencimiento(self):
        if self.fecha_vencimiento:
            dias = (self.fecha_vencimiento - timezone.now().date()).days
            return dias <= 30
        return False

    @property
    def margen(self):
        if self.precio_compra > 0:
            return round(((self.precio_venta - self.precio_compra) / self.precio_compra) * 100, 2)
        return 0


class Movimiento(TimeStampedModel):
    # Tipos de movimiento
    ENTRADA_COMPRA = 'EC'
    SALIDA_VENTA = 'SV'
    AJUSTE_POSITIVO = 'AP'
    AJUSTE_NEGATIVO = 'AN'
    DEVOLUCION_ENTRADA = 'DE'
    DEVOLUCION_SALIDA = 'DS'

    TIPO_CHOICES = (
        (ENTRADA_COMPRA, 'Entrada por Compra'),
        (SALIDA_VENTA, 'Salida por Venta'),
        (AJUSTE_POSITIVO, 'Ajuste Positivo'),
        (AJUSTE_NEGATIVO, 'Ajuste Negativo'),
        (DEVOLUCION_ENTRADA, 'Devolución Entrada'),
        (DEVOLUCION_SALIDA, 'Devolución Salida'),
    )

    TIPOS_ENTRADA = [ENTRADA_COMPRA, AJUSTE_POSITIVO, DEVOLUCION_ENTRADA]
    TIPOS_SALIDA = [SALIDA_VENTA, AJUSTE_NEGATIVO, DEVOLUCION_SALIDA]

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        related_name='movimientos', verbose_name='Producto'
    )
    tipo = models.CharField('Tipo', max_length=2, choices=TIPO_CHOICES)
    cantidad = models.IntegerField('Cantidad')
    stock_anterior = models.IntegerField('Stock Anterior')
    stock_posterior = models.IntegerField('Stock Posterior')
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=12, decimal_places=2, default=0)
    motivo = models.TextField('Motivo / Referencia', blank=True)
    documento_referencia = models.CharField('N° Documento', max_length=50, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimientos', verbose_name='Usuario'
    )
    fecha = models.DateTimeField('Fecha', default=timezone.now)

    objects = MovimientoManager()

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.producto} ({self.cantidad})'

    @property
    def es_entrada(self):
        return self.tipo in self.TIPOS_ENTRADA

    @property
    def total(self):
        return self.cantidad * self.precio_unitario


class AjusteInventario(TimeStampedModel):
    PENDIENTE = 'P'
    APROBADO = 'A'
    RECHAZADO = 'R'
    ESTADO_CHOICES = (
        (PENDIENTE, 'Pendiente'),
        (APROBADO, 'Aprobado'),
        (RECHAZADO, 'Rechazado'),
    )

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        related_name='ajustes', verbose_name='Producto'
    )
    cantidad_sistema = models.IntegerField('Cantidad en Sistema')
    cantidad_fisica = models.IntegerField('Cantidad Física')
    diferencia = models.IntegerField('Diferencia')
    motivo = models.TextField('Motivo')
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default=PENDIENTE)
    solicitado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ajustes_solicitados',
        verbose_name='Solicitado por'
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='ajustes_aprobados',
        verbose_name='Aprobado por'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    movimiento = models.OneToOneField(
        Movimiento, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ajuste', verbose_name='Movimiento generado'
    )

    class Meta:
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'
        ordering = ['-created']

    def __str__(self):
        return f'Ajuste {self.producto} ({self.get_estado_display()})'

    def save(self, *args, **kwargs):
        self.diferencia = self.cantidad_fisica - self.cantidad_sistema
        super().save(*args, **kwargs)


class Alerta(TimeStampedModel):
    STOCK_MINIMO = 'SM'
    STOCK_MAXIMO = 'SX'
    VENCIMIENTO = 'VE'
    SIN_MOVIMIENTO = 'SI'

    TIPO_CHOICES = (
        (STOCK_MINIMO, 'Stock Mínimo'),
        (STOCK_MAXIMO, 'Stock Máximo'),
        (VENCIMIENTO, 'Vencimiento Próximo'),
        (SIN_MOVIMIENTO, 'Sin Movimiento'),
    )

    BAJA = '1'
    MEDIA = '2'
    ALTA = '3'
    PRIORIDAD_CHOICES = (
        (BAJA, 'Baja'),
        (MEDIA, 'Media'),
        (ALTA, 'Alta'),
    )

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE,
        related_name='alertas', verbose_name='Producto'
    )
    tipo = models.CharField('Tipo', max_length=2, choices=TIPO_CHOICES)
    prioridad = models.CharField('Prioridad', max_length=1, choices=PRIORIDAD_CHOICES, default=MEDIA)
    mensaje = models.TextField('Mensaje')
    resuelta = models.BooleanField('Resuelta', default=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    objects = AlertaManager()

    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-created', 'prioridad']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.producto}'