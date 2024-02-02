from django import forms
from .models import Proveedor
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from crispy_forms.bootstrap import FormActions


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'imagen',
            'nif',
            'nombre',
            'calle',
            'ciudad',
            'provincia',
            'codigo_postal',
            'email',
            'telefono'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(
                HTML(
                    """{% if imagen %} 
                    <img id="miniatura" class="img-responsive" 
                    src="{{ imagen.url }}" style="padding: 10px; border-radius: 50%; height: 175px; width: 
                    175px;"> 
                    {% else %}
                    <img id="miniatura" class="img-responsive" 
                    src="/media/user.png" style="padding: 10px; border-radius: 50%; height: 175px; width: 
                    175px;"> 
                    {% endif %}"""),
                Column('imagen', css_class='form-group col-md-6 mb-2'),
                css_class='align-items-end mb-4'
            ),
            Row(
                Column('nif', css_class='form-group col-md-6 mb-4'),
                Column('nombre', css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column('calle', css_class='form-group col-md-6 mb-4'),
                Column('ciudad', css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column('provincia', css_class='form-group col-md-6 mb-4'),
                Column('codigo_postal', css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-4'),
                Column('telefono', css_class='form-group col-md-6 mb-4'),
            ),
            FormActions(
                Div(
                    Row(
                        Column(Submit('submit', 'Guardar proveedor')),
                        Column(HTML('<a class="btn btn-danger" href="/proveedores">Cancelar</a>')),
                    ),
                    css_class='row justify-content-left ml-4'
                )
            )
        )
