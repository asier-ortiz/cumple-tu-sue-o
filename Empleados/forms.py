from django import forms
from .models import Departamento, Empleado
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from crispy_forms.bootstrap import FormActions, TabHolder, Tab


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = [
            'nombre'
        ]


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'fotografia',
            'nombre',
            'apellidos',
            'email',
            'telefono',
            'departamento',
            'responsable',
            'dni',
            'sexo',
            'estado_civil',
            'fecha_nacimiento',
            'nombre_usuario',
            'contraseña',
            'fecha_contratacion',
            'activo',
            'otra_informacion'
        ]
        widgets = {
            'fecha_contratacion': DateTimePickerInput(),
            'fecha_nacimiento': DateTimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Información del trabajo',
                    Row(
                        HTML(
                            """{% if fotografia %} 
                            <img id="miniatura" class="img-responsive" 
                            src="{{ fotografia.url }}" style="padding: 10px; border-radius: 50%; height: 175px; width: 
                            175px;"> 
                            {% else %}
                            <img id="miniatura" class="img-responsive" 
                            src="/media/user.png" style="padding: 10px; border-radius: 50%; height: 175px; width: 
                            175px;"> 
                            {% endif %}"""),
                        Column('fotografia', css_class='form-group col-md-6 mb-2'),
                        css_class='align-items-end mb-4'
                    ),
                    Row(
                        Column('nombre', css_class='form-group col-md-6 mb-4'),
                        Column('apellidos', css_class='form-group col-md-6 mb-4')
                    ),
                    Row(
                        Column('email', css_class='form-group col-md-6 mb-4'),
                        Column('telefono', css_class='form-group col-md-6 mb-4')
                    ),
                    Row(
                        Column('departamento', css_class='form-group col-md-6 mb-4'),
                        Column('responsable', css_class='form-group col-md-6 mb-4')
                    )
                    ),
                Tab('Información Privada',
                    Row(Column('dni', css_class='form-group mb-4')),
                    Row(Column('sexo', css_class='form-group mb-4')),
                    Row(Column('estado_civil', css_class='form-group mb-4')),
                    Row(Column('fecha_nacimiento', css_class='form-group mb-4'))
                    ),
                Tab('Configuración de RRHH',
                    Row(Column('nombre_usuario', css_class='form-group mb-4')),
                    Row(Column('contraseña', css_class='form-group mb-4')),
                    Row(Column('fecha_contratacion', css_class='form-group mb-4')),
                    Row(Column('activo', css_class='form-group mb-4')),
                    Row(Column('otra_informacion', css_class='form-group mb-4'))
                    ),
            ),
            FormActions(
                Div(
                    Row(
                        Column(Submit('submit', 'Guardar empleado')),
                        Column(HTML('<a class="btn btn-danger" href="/empleados">Cancelar</a>')),
                    ),
                    css_class='row justify-content-left ml-4'
                )
            ),
        )


class EmpleadoContraseñaForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'contraseña'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = "font-weight-bold"
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(Column('contraseña', css_class='form-group mb-4')),
            FormActions(
                Div(
                    Row(
                        Column(Submit('submit', 'Guardar empleado')),
                        Column(HTML('<a class="btn btn-danger" href="/empleados" onclick="goBack()">Cancelar</a>')),
                    ),
                    css_class='row justify-content-left ml-4'
                )
            )
        )
