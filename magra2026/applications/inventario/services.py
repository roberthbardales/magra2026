from django.utils import timezone
from django.db import transaction
from .models import Producto, Movimiento, AjusteInventario, Alerta


class InventarioService:
    """Servicio central para operaciones de inventario."""

    @staticmethod
    @transaction.atomic
    def registrar_movimiento(producto, tipo, cantidad, usuario,
                              precio_unitario=None, motivo='', documento=''):
        """Registra un movimiento y actualiza el stock del producto."""

        stock_anterior = producto.stock_actual

        if tipo in Movimiento.TIPOS_ENTRADA:
            stock_posterior = stock_anterior + cantidad
        else:
            if cantidad > stock_anterior:
                raise ValueError(
                    f'Stock insuficiente. Stock actual: {stock_anterior}, '
                    f'cantidad solicitada: {cantidad}'
                )
            stock_posterior = stock_anterior - cantidad

        movimiento = Movimiento.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_posterior=stock_posterior,
            precio_unitario=precio_unitario or producto.precio_compra,
            motivo=motivo,
            documento_referencia=documento,
            usuario=usuario,
        )

        producto.stock_actual = stock_posterior
        producto.save(update_fields=['stock_actual', 'modified'])

        # Generar alertas automáticas después del movimiento
        AlertaService.verificar_alertas(producto)

        return movimiento

    @staticmethod
    @transaction.atomic
    def aprobar_ajuste(ajuste, usuario_aprobador):
        """Aprueba un ajuste de inventario y genera el movimiento correspondiente."""

        if ajuste.estado != AjusteInventario.PENDIENTE:
            raise ValueError('Solo se pueden aprobar ajustes en estado Pendiente.')

        diferencia = ajuste.diferencia
        if diferencia == 0:
            ajuste.estado = AjusteInventario.APROBADO
            ajuste.aprobado_por = usuario_aprobador
            ajuste.fecha_aprobacion = timezone.now()
            ajuste.save()
            return ajuste

        tipo = Movimiento.AJUSTE_POSITIVO if diferencia > 0 else Movimiento.AJUSTE_NEGATIVO
        cantidad = abs(diferencia)

        movimiento = InventarioService.registrar_movimiento(
            producto=ajuste.producto,
            tipo=tipo,
            cantidad=cantidad,
            usuario=usuario_aprobador,
            motivo=f'Ajuste de inventario aprobado. {ajuste.motivo}',
        )

        ajuste.estado = AjusteInventario.APROBADO
        ajuste.aprobado_por = usuario_aprobador
        ajuste.fecha_aprobacion = timezone.now()
        ajuste.movimiento = movimiento
        ajuste.save()

        return ajuste

    @staticmethod
    @transaction.atomic
    def rechazar_ajuste(ajuste, usuario):
        if ajuste.estado != AjusteInventario.PENDIENTE:
            raise ValueError('Solo se pueden rechazar ajustes en estado Pendiente.')
        ajuste.estado = AjusteInventario.RECHAZADO
        ajuste.aprobado_por = usuario
        ajuste.fecha_aprobacion = timezone.now()
        ajuste.save()
        return ajuste


class AlertaService:
    """Servicio para generación y gestión de alertas."""

    @staticmethod
    def verificar_alertas(producto):
        """Verifica todas las condiciones de alerta para un producto."""
        AlertaService._verificar_stock_minimo(producto)
        AlertaService._verificar_stock_maximo(producto)
        AlertaService._verificar_vencimiento(producto)

    @staticmethod
    def _verificar_stock_minimo(producto):
        if producto.stock_actual <= producto.stock_minimo:
            # Evitar duplicados: solo crear si no existe activa
            if not Alerta.objects.filter(
                producto=producto,
                tipo=Alerta.STOCK_MINIMO,
                resuelta=False
            ).exists():
                Alerta.objects.create(
                    producto=producto,
                    tipo=Alerta.STOCK_MINIMO,
                    prioridad=Alerta.ALTA,
                    mensaje=(
                        f'El producto "{producto.nombre}" tiene stock bajo. '
                        f'Stock actual: {producto.stock_actual}, '
                        f'mínimo: {producto.stock_minimo}.'
                    )
                )
        else:
            # Resolver alertas previas si el stock ya superó el mínimo
            Alerta.objects.filter(
                producto=producto,
                tipo=Alerta.STOCK_MINIMO,
                resuelta=False
            ).update(resuelta=True, fecha_resolucion=timezone.now())

    @staticmethod
    def _verificar_stock_maximo(producto):
        if producto.stock_actual >= producto.stock_maximo:
            if not Alerta.objects.filter(
                producto=producto,
                tipo=Alerta.STOCK_MAXIMO,
                resuelta=False
            ).exists():
                Alerta.objects.create(
                    producto=producto,
                    tipo=Alerta.STOCK_MAXIMO,
                    prioridad=Alerta.MEDIA,
                    mensaje=(
                        f'El producto "{producto.nombre}" superó el stock máximo. '
                        f'Stock actual: {producto.stock_actual}, '
                        f'máximo: {producto.stock_maximo}.'
                    )
                )
        else:
            Alerta.objects.filter(
                producto=producto,
                tipo=Alerta.STOCK_MAXIMO,
                resuelta=False
            ).update(resuelta=True, fecha_resolucion=timezone.now())

    @staticmethod
    def _verificar_vencimiento(producto):
        from datetime import timedelta
        if producto.fecha_vencimiento:
            dias = (producto.fecha_vencimiento - timezone.now().date()).days
            if dias <= 30:
                if not Alerta.objects.filter(
                    producto=producto,
                    tipo=Alerta.VENCIMIENTO,
                    resuelta=False
                ).exists():
                    prioridad = Alerta.ALTA if dias <= 7 else Alerta.MEDIA
                    Alerta.objects.create(
                        producto=producto,
                        tipo=Alerta.VENCIMIENTO,
                        prioridad=prioridad,
                        mensaje=(
                            f'El producto "{producto.nombre}" vence en {dias} días '
                            f'({producto.fecha_vencimiento}).'
                        )
                    )

    @staticmethod
    def generar_alertas_sin_movimiento(dias=30):
        """Tarea para ejecutar periódicamente (cron/celery)."""
        from django.utils import timezone
        from datetime import timedelta
        productos = Producto.objects.sin_movimiento(dias=dias)
        for producto in productos:
            if not Alerta.objects.filter(
                producto=producto,
                tipo=Alerta.SIN_MOVIMIENTO,
                resuelta=False
            ).exists():
                Alerta.objects.create(
                    producto=producto,
                    tipo=Alerta.SIN_MOVIMIENTO,
                    prioridad=Alerta.BAJA,
                    mensaje=(
                        f'El producto "{producto.nombre}" no tiene movimientos '
                        f'en los últimos {dias} días.'
                    )
                )
