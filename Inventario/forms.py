from django import forms
from .models import Producto
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div
from crispy_forms.bootstrap import PrependedAppendedText, FormActions


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'imagen',
            'precio_venta',
            'precio_coste',
            'iva_cobrar',
            'iva_pagar',
            'cantidad_disponible',
            'proveedor'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"
        self.helper.form_method = 'POST'
        self.fields['precio_venta'].widget.attrs['min'] = 0.0
        self.fields['precio_venta'].widget.attrs['min'] = 0.0
        self.fields['iva_cobrar'].widget.attrs['min'] = 0.0
        self.fields['iva_pagar'].widget.attrs['min'] = 0.0
        self.fields['cantidad_disponible'].widget.attrs['min'] = 0
        self.helper.layout = Layout(
            Row(
                HTML(
                    """{% if imagen %} 
                    <img id="miniatura" class="img-responsive" 
                    src="{{ imagen.url }}" style="padding: 10px; height: 175px; width: 
                    175px;"> 
                    {% else %}
                    <img id="miniatura" class="img-responsive" 
                    src="/media/dress.png" style="padding: 10px; height: 175px; width: 
                    175px;"> 
                    {% endif %}"""),
                Column('imagen', css_class='form-group col-md-6 mb-2'),
                css_class='align-items-end mb-4'
            ),
            Row(
                Column('nombre', css_class='form-group col-md-6 mb-4'),
                Column('proveedor', css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column(PrependedAppendedText('precio_venta', '', '€'), css_class='form-group col-md-6 mb-4'),
                Column(PrependedAppendedText('precio_coste', '', '€'), css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column(PrependedAppendedText('iva_cobrar', '', '%'), css_class='form-group col-md-6 mb-4'),
                Column(PrependedAppendedText('iva_pagar', '', '%'), css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column('cantidad_disponible', css_class='form-group col-md-6 mb-4'),
            ),
            FormActions(
                Div(
                    Row(
                        Column(Submit('submit', 'Guardar producto')),
                        Column(HTML('<a class="btn btn-danger" href="/inventario">Cancelar</a>')),
                    ),
                    css_class='row justify-content-left ml-4'
                )
            )
        )
