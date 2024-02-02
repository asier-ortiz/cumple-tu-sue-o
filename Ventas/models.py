from django.db import models
from Empleados.models import Empleado
from Inventario.models import Producto
from django.core.validators import MinValueValidator


class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    nif = models.CharField(primary_key=True, max_length=7)
    calle = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=30)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    imagen = models.ImageField(blank=True, null=True, default="/user.png")

    def calcular_gasto_total_por_cliente(self):
        total = 0
        pedidos = Pedido.objects.filter(cliente=self)
        for pedido in pedidos:
            total += pedido.calcular_total()
        return total

    def calcular_numero_compras_por_cliente(self):
        return len(Pedido.objects.filter(cliente=self))


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, on_delete=models.SET_NULL)
    comercial = models.ForeignKey(Empleado, null=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    productos = models.ManyToManyField(Producto, through='LineaPedido')

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
        return Pedido.objects.get(pk=id).lineapedido_set.values('cantidad').filter(producto=producto)[0]

    def lineas(self):
        lineas = []
        for producto in self.productos.distinct():
            cantidad = self.calcular_cantidad(self.pk, producto=producto).get('cantidad')
            iva = (producto.precio_venta * producto.iva_cobrar) / 100
            lineas.append((producto.nombre, cantidad,
                           producto.precio_venta,
                           producto.iva_cobrar, (producto.precio_venta + iva) * cantidad,
                           producto.precio_venta * cantidad, iva * cantidad))
        return lineas


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, null=True, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, null=True, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1, validators=[MinValueValidator(1)])
