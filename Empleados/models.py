import datetime
from itertools import chain
from typing import Iterable

from ckeditor_uploader.fields import RichTextUploadingField
from treelib import Tree
from django.db import models
from model_utils import Choices
from django.conf import settings


# SUPER USER: name: Asier, password: Asier12345Abcde

class Departamento(models.Model):
    nombre = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    SEXO = Choices('Hombre', 'Mujer', 'Otro')
    ESTADO_CIVIL = Choices('Soltero', 'Casado', 'Viudo', 'Divorciado')
    ACTIVO = Choices((True, 'Si'), (False, 'No'))
    fotografia = models.ImageField(blank=True, null=True, default="/user.png")
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    departamento = models.ForeignKey(Departamento, null=True, blank=True, on_delete=models.SET_NULL)
    responsable = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    dni = models.CharField(primary_key=True, max_length=9)
    sexo = models.CharField(choices=SEXO, max_length=10)
    estado_civil = models.CharField(choices=ESTADO_CIVIL, max_length=10)
    fecha_nacimiento = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    nombre_usuario = models.CharField(max_length=50, null=True, unique=True)
    contraseña = models.CharField(max_length=20, null=True)
    fecha_contratacion = models.DateField(default=datetime.date.today)
    activo = models.BooleanField(choices=ACTIVO, default=True)
    otra_informacion = RichTextUploadingField(blank=True, null=True)

    def __str__(self):
        return "%s %s" % (
            self.nombre, self.apellidos)

    def get_descendats_ids(self):
        return (empleado.dni for empleado in list(self.get_descendats(self)))

    def get_descendats(self, empleado: 'Empleado') -> Iterable['Empleado']:
        queryset = Empleado.objects.filter(responsable=empleado)
        results = chain(queryset)
        for child in queryset:
            results = chain(results, self.get_descendats(child))
        return results

    def get_ascestors(self, empleado: 'Empleado') -> Iterable['Empleado']:
        if empleado.responsable:
            return chain([empleado.responsable], self.get_ascestors(empleado.responsable))
        return chain()

    def generate_tree(self):
        asc = list(self.get_ascestors(self))
        asc = asc[::-1]
        des = list(self.get_descendats(self))
        des.insert(0, self)
        all = list(chain(asc, des))
        tree = Tree()
        tree.create_node(all[0].nombre, all[0].nombre)
        all.remove(all[0])
        for empleado in all:
            tree.create_node(empleado.nombre, empleado.nombre, parent=empleado.responsable.nombre)
        return tree

    def calcular_recaudacion_total_por_comercial(self):
        from Ventas.models import Pedido
        total = 0
        pedidos = Pedido.objects.filter(comercial=self)
        for pedido in pedidos:
            total += pedido.calcular_total()
        return total

    def calcular_numero_ventas_por_comercial(self):
        from Ventas.models import Pedido
        return len(Pedido.objects.filter(comercial=self))

    def calcular_gasto_total_por_comercial(self):
        from Compras.models import Compra
        total = 0
        compras = Compra.objects.filter(comercial=self)
        for compra in compras:
            total += compra.calcular_total()
        return total

    def calcular_numero_compras_por_comercial(self):
        from Compras.models import Compra
        return len(Compra.objects.filter(comercial=self))
