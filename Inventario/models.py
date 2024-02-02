from django.db import models
from django.core.validators import MinValueValidator


class Producto(models.Model):
    nombre = models.CharField(primary_key=True, max_length=50)
    imagen = models.ImageField(blank=True, null=True, default="/dress.png")
    precio_venta = models.FloatField(validators=[MinValueValidator(1.00)])
    precio_coste = models.FloatField(default=0.00, blank=True, null=True, validators=[MinValueValidator(0.00)])
    iva_cobrar = models.FloatField(default=21.0, validators=[MinValueValidator(1.00)])
    iva_pagar = models.FloatField(default=21.0, validators=[MinValueValidator(1.00)])
    cantidad_disponible = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    proveedor = models.ForeignKey('Compras.Proveedor', null=True, on_delete=models.SET_NULL)

    def actualizar_cantidad_restar(self, cantidad):
        Producto.objects.filter(pk=self.pk).update(cantidad_disponible=self.cantidad_disponible - cantidad)

    def actualizar_cantidad_agregar(self, cantidad):
        Producto.objects.filter(pk=self.pk).update(cantidad_disponible=self.cantidad_disponible + cantidad)
