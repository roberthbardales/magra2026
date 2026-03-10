from django import forms
from .models import (
    UnidadMedida, Categoria, Proveedor,
    Almacen, Producto, Movimiento, AjusteInventario
)

BOOTSTRAP_INPUT = 'form-control'
BOOTSTRAP_SELECT = 'form-control'
BOOTSTRAP_TEXTAREA = 'form-control'
BOOTSTRAP_CHECK = 'form-check-input'


class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ['nombre', 'abreviatura', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT, 'placeholder': 'Ej: Kilogramo'}),
            'abreviatura': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT, 'placeholder': 'Ej: kg'}),
            'activo': forms.CheckboxInput(attrs={'class': BOOTSTRAP_CHECK}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT, 'placeholder': 'Nombre de categoría'}),
            'descripcion': forms.Textarea(attrs={'class': BOOTSTRAP_TEXTAREA, 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': BOOTSTRAP_CHECK}),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social', 'ruc', 'contacto', 'telefono', 'email', 'direccion', 'activo']
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT}),
            'ruc': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT}),
            'contacto': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT}),
            'telefono': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT}),
            'email': forms.EmailInput(attrs={'class': BOOTSTRAP_INPUT}),
            'direccion': forms.Textarea(attrs={'class': BOOTSTRAP_TEXTAREA, 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': BOOTSTRAP_CHECK}),
        }


class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'descripcion', 'responsable', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT}),
            'descripcion': forms.Textarea(attrs={'class': BOOTSTRAP_TEXTAREA, 'rows': 3}),
            'responsable': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'activo': forms.CheckboxInput(attrs={'class': BOOTSTRAP_CHECK}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'sku', 'nombre', 'descripcion', 'categoria', 'unidad_medida',
            'proveedor', 'almacen', 'precio_compra', 'precio_venta',
            'stock_minimo', 'stock_maximo', 'fecha_vencimiento', 'imagen', 'estado'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT, 'placeholder': 'Ej: PROD-001'}),
            'nombre': forms.TextInput(attrs={'class': BOOTSTRAP_INPUT}),
            'descripcion': forms.Textarea(attrs={'class': BOOTSTRAP_TEXTAREA, 'rows': 3}),
            'categoria': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'unidad_medida': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'proveedor': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'almacen': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'precio_compra': forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT, 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT, 'step': '0.01'}),
            'stock_minimo': forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT}),
            'stock_maximo': forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': BOOTSTRAP_INPUT, 'type': 'date'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'estado': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
        }

    def clean(self):
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get('precio_compra')
        precio_venta = cleaned_data.get('precio_venta')
        stock_minimo = cleaned_data.get('stock_minimo')
        stock_maximo = cleaned_data.get('stock_maximo')

        if precio_compra and precio_venta:
            if precio_venta < precio_compra:
                self.add_error('precio_venta', 'El precio de venta no puede ser menor al precio de compra.')

        if stock_minimo is not None and stock_maximo is not None:
            if stock_minimo >= stock_maximo:
                self.add_error('stock_maximo', 'El stock máximo debe ser mayor al stock mínimo.')

        return cleaned_data


class EntradaStockForm(forms.Form):
    """Formulario para registrar entrada de stock (compra o devolución)."""
    TIPO_CHOICES = (
        ('EC', 'Entrada por Compra'),
        ('DE', 'Devolución Entrada'),
    )
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': BOOTSTRAP_SELECT})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT})
    )
    precio_unitario = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT, 'step': '0.01'})
    )
    documento_referencia = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': BOOTSTRAP_INPUT, 'placeholder': 'N° Factura / Guía'})
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': BOOTSTRAP_TEXTAREA, 'rows': 2})
    )


class SalidaStockForm(forms.Form):
    """Formulario para registrar salida de stock (venta o devolución)."""
    TIPO_CHOICES = (
        ('SV', 'Salida por Venta'),
        ('DS', 'Devolución Salida'),
    )
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': BOOTSTRAP_SELECT})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT})
    )
    precio_unitario = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT, 'step': '0.01'})
    )
    documento_referencia = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': BOOTSTRAP_INPUT, 'placeholder': 'N° Factura / Boleta'})
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': BOOTSTRAP_TEXTAREA, 'rows': 2})
    )

    def __init__(self, producto=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producto = producto

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if self.producto and cantidad > self.producto.stock_actual:
            raise forms.ValidationError(
                f'Stock insuficiente. Disponible: {self.producto.stock_actual}'
            )
        return cantidad


class AjusteInventarioForm(forms.ModelForm):
    class Meta:
        model = AjusteInventario
        fields = ['producto', 'cantidad_fisica', 'motivo']
        widgets = {
            'producto': forms.Select(attrs={'class': BOOTSTRAP_SELECT}),
            'cantidad_fisica': forms.NumberInput(attrs={'class': BOOTSTRAP_INPUT, 'min': '0'}),
            'motivo': forms.Textarea(attrs={'class': BOOTSTRAP_TEXTAREA, 'rows': 3,
                                            'placeholder': 'Explique el motivo del ajuste...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.activos()


class FiltroMovimientoForm(forms.Form):
    """Formulario de filtros para el historial de movimientos."""
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.activos(),
        required=False,
        empty_label='Todos los productos',
        widget=forms.Select(attrs={'class': BOOTSTRAP_SELECT})
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + list(Movimiento.TIPO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': BOOTSTRAP_SELECT})
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': BOOTSTRAP_INPUT, 'type': 'date'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': BOOTSTRAP_INPUT, 'type': 'date'})
    )