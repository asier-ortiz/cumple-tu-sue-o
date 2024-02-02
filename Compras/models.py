from django.db import models
from Empleados.models import Empleado
from Inventario.models import Producto
from django.core.validators import MinValueValidator


class Proveedor(models.Model):
    nombre = models.CharField(max_length=50)
    nif = models.CharField(primary_key=True, max_length=7)
    calle = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=30)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    imagen = models.ImageField(blank=True, null=True, default="/user.png")

    def __str__(self):
        return self.nombre

    def calcular_gasto_total_por_proveedor(self):
        total = 0
        compras = Compra.objects.filter(proveedor=self)
        for compra in compras:
            total += compra.calcular_total()
        return total

    def calcular_numero_compras_por_proveedor(self):
        return len(Compra.objects.filter(proveedor=self))


class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, null=True, on_delete=models.SET_NULL)
    comercial = models.ForeignKey(Empleado, null=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    productos = models.ManyToManyField(Producto, through='LineaCompra')

    def calcular_total(self):
        total = 0.0
        for linea in self.lineas():
            total += linea[4]
        return total

    def calcular_subotal(self):
        subtotal = 0.0
        for linea in self.lineas():
            subtotal += linea[5]
        return subtotal

    def calcular_iva(self):
        iva = 0.0
        for linea in self.lineas():
            iva += linea[6]
        return iva

    def calcular_cantidad(self, id, producto):
        return Compra.objects.get(pk=id).lineacompra_set.values('cantidad').filter(producto=producto)[0]

    def lineas(self):
        lineas = []
        for producto in self.productos.distinct():
            cantidad = self.calcular_cantidad(self.pk, producto=producto).get('cantidad')
            iva = (producto.precio_coste * producto.iva_pagar) / 100
            lineas.append((producto.nombre, cantidad,
                           producto.precio_coste,
                           producto.iva_pagar, (producto.precio_coste + iva) * cantidad,
                           producto.precio_coste * cantidad, iva * cantidad))
        return lineas


class LineaCompra(models.Model):
    compra = models.ForeignKey(Compra, null=True, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=True, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1, validators=[MinValueValidator(1)])
