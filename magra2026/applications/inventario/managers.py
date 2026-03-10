from django.db import models
from django.utils import timezone
from datetime import timedelta


class ProductoManager(models.Manager):

    def activos(self):
        return self.filter(estado='A')

    def con_stock_minimo(self):
        return self.filter(
            estado='A',
            stock_actual__lte=models.F('stock_minimo')
        )

    def con_stock_maximo(self):
        return self.filter(
            estado='A',
            stock_actual__gte=models.F('stock_maximo')
        )

    def por_vencer(self, dias=30):
        limite = timezone.now().date() + timedelta(days=dias)
        return self.filter(
            estado='A',
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lte=limite
        )

    def sin_movimiento(self, dias=30):
        limite = timezone.now() - timedelta(days=dias)
        return self.filter(
            estado='A'
        ).exclude(
            movimientos__fecha__gte=limite
        )

    def buscar(self, query):
        return self.filter(
            models.Q(sku__icontains=query) |
            models.Q(nombre__icontains=query) |
            models.Q(descripcion__icontains=query)
        )


class MovimientoManager(models.Manager):

    def entradas(self):
        return self.filter(tipo__in=['EC', 'AP', 'DE'])

    def salidas(self):
        return self.filter(tipo__in=['SV', 'AN', 'DS'])

    def por_producto(self, producto_id):
        return self.filter(producto_id=producto_id).order_by('-fecha')

    def por_rango_fecha(self, fecha_inicio, fecha_fin):
        return self.filter(fecha__date__range=[fecha_inicio, fecha_fin])

    def del_mes(self):
        hoy = timezone.now()
        return self.filter(
            fecha__year=hoy.year,
            fecha__month=hoy.month
        )


class AlertaManager(models.Manager):

    def activas(self):
        return self.filter(resuelta=False)

    def altas(self):
        return self.filter(resuelta=False, prioridad='3')

    def por_tipo(self, tipo):
        return self.filter(resuelta=False, tipo=tipo)

    def count_activas(self):
        return self.filter(resuelta=False).count()