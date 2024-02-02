from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
import csv
import io
from django.contrib import messages
from Compras.models import Proveedor
from Inventario.models import Producto
from .forms import ProductoForm
from django.contrib.auth.models import Group
from django.db.models import Q


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def productos(request):
    productos = Producto.objects.order_by('nombre')
    proveedores = Proveedor.objects.order_by('nombre')
    paginator = Paginator(productos, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventario/index.html', {'page_obj': page_obj, 'proveedores': proveedores})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            imagen = request.FILES.get('imagen')
            if imagen is not None:
                new.imagen = imagen
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/crear_producto.html', {'form': form})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def modificar_producto(request, nombre):
    producto = Producto.objects.get(nombre=nombre)
    form = ProductoForm(request.POST or None, instance=producto)
    form.fields['nombre'].widget.attrs['readonly'] = True
    if form.is_valid():
        new = form.save(commit=False)
        if request.FILES.get('imagen') is not None:
            new.imagen = request.FILES.get('imagen', default="/dress.png")
        form.save()
        return redirect('productos')
    return render(request, 'inventario/crear_producto.html',
                  {'form': form, 'nombre': producto.nombre, 'imagen': producto.imagen})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def borrar_producto(request, nombre):
    producto = Producto.objects.get(nombre=nombre)
    producto.delete()
    return redirect('productos')


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def buscar_producto(request):
    nombre = request.POST.get('nombre')
    id_proveedor = request.POST.get('proveedor_select')
    stock = request.POST.get('stock')
    proveedores = Proveedor.objects.order_by('nombre')
    if stock == "True":
        page_obj = Producto.objects.filter(
            Q(nombre__contains=nombre),
            Q(proveedor__nif=id_proveedor),
            Q(cantidad_disponible__gte=1)
        )
    else:
        page_obj = Producto.objects.filter(
            Q(nombre__contains=nombre),
            Q(proveedor__nif=id_proveedor),
            Q(cantidad_disponible__lte=0)
        )
    return render(request, 'inventario/index.html', {'page_obj': page_obj, 'proveedores': proveedores})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def importar_productos(request):
    template = "inventario/importar_productos.html"
    prompt = {
        'order': 'Orden del fichero CSV: Nombre, Proveedor {nif}, Precio venta, Precio coste, Iva cobrar, Iva pagar, Cantidad disponible'
    }
    if request.method == 'GET':
        return render(request, template, prompt)
    try:
        csv_file = request.FILES['file']
    except MultiValueDictKeyError:
        messages.error(request, 'Debe seleccionar un fichero')
        return render(request, template, prompt)
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'Debe seleccionar un fichero CSV')
        return render(request, template, prompt)
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar='|'):
        try:
            proveedor = Proveedor.objects.get(nif=column[1])
        except Proveedor.DoesNotExist:
            proveedor = None
        Producto.objects.update_or_create(
            nombre=column[0],
            proveedor=proveedor,
            precio_venta=column[2],
            precio_coste=column[3],
            iva_cobrar=column[4],
            iva_pagar=column[5],
            cantidad_disponible=column[6]
        )
    return render(request, template)


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def exportar_productos(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(
        ['Nombre', 'Proveedor', 'Precio venta', 'Precio coste', 'Iva cobrar', 'Iva pagar', 'Cantidad disponible'])

    for producto in Producto.objects.all().values_list('nombre', 'proveedor', 'precio_venta', 'precio_coste',
                                                       'iva_cobrar', 'iva_pagar', 'cantidad_disponible'):
        writer.writerow(producto)
    response['Content-Disposition'] = 'attachment; filename="empleados.csv"'
    return response
