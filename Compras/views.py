import numpy as np
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
import io
import csv
import matplotlib.pyplot as plt
import base64
from django.contrib import messages
from Compras.forms import ProveedorForm
from Compras.models import Proveedor, Compra, LineaCompra
from Empleados.models import Empleado
from Inventario.models import Producto


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def compras(request):
    compras = Compra.objects.order_by('-fecha')
    paginator = Paginator(compras, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'compras/compras/index.html', {'page_obj': page_obj})


@csrf_exempt
@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def crear_compra(request):
    proveedor_select = request.POST.get('proveedor_select')
    proveedor_nombre = request.POST.get('proveedor')
    arr = request.POST.getlist('arr[]')
    if request.method == "POST":
        if arr:
            diccionario = dict(zip(arr[::2], arr[1::2]))
            proveedor = get_object_or_404(Proveedor, nombre=proveedor_nombre)
            user = request.user
            comercial = get_object_or_404(Empleado, user=user)
            Compra(comercial=comercial, proveedor=proveedor).save()
            compra = Compra.objects.last()
            for k, v in diccionario.items():
                producto = get_object_or_404(Producto, pk=k)
                producto.actualizar_cantidad_agregar(int(v))
                LineaCompra(compra=compra, producto=producto, cantidad=int(v)).save()
            return redirect('compras')
        elif proveedor_select:
            productos = Producto.objects.all().filter(proveedor=proveedor_select).filter(cantidad_disponible__gte=1)
            paginator = Paginator(productos, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'compras/compras/crear_compra.html', {
                'proveedores': Proveedor.objects.all(),
                'page_obj': page_obj})
    return render(request, 'compras/compras/crear_compra.html', {
        'proveedores': Proveedor.objects.all()})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def ver_detalle_compra(request, id):
    return render(request, 'compras/compras/detalle_compra.html', {'compra': Compra.objects.get(pk=id)})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def borrar_compra(request, id):
    compra = Compra.objects.get(pk=id)
    compra.delete()
    return redirect('compras')


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def proveedores(request):
    proveedores = Proveedor.objects.order_by('nombre')
    paginator = Paginator(proveedores, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'compras/proveedores/index.html', {'page_obj': page_obj})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def crear_proveedor(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.imagen = request.FILES.get('imagen')
            form.save()
            return redirect('proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'compras/proveedores/crear_proveedor.html', {'form': form})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def modificar_proveedor(request, nif):
    proveedor = get_object_or_404(Proveedor, nif=nif)
    form = ProveedorForm(request.POST or None, instance=proveedor)
    form.fields['nif'].widget.attrs['readonly'] = True
    if form.is_valid():
        new = form.save(commit=False)
        if request.FILES.get('imagen') is not None:
            new.imagen = request.FILES.get('imagen', default="/user.png")
        form.save()
        return redirect('proveedores')
    return render(request, 'compras/proveedores/crear_proveedor.html',
                  {'form': form, 'nif': proveedor.nif, 'imagen': proveedor.imagen})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def borrar_proveedor(request, nif):
    proveedor = get_object_or_404(Proveedor, nif=nif)
    proveedor.delete()
    return redirect('proveedores')


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def buscar_proveedor(request):
    nif = request.POST.get('nif')
    nombre = request.POST.get('nombre')
    ciudad = request.POST.get('ciudad')
    provincia = request.POST.get('provincia')
    email = request.POST.get('email')
    telefono = request.POST.get('telefono')
    page_obj = Proveedor.objects.filter(
        Q(nif__contains=nif),
        Q(nombre__contains=nombre),
        Q(ciudad__contains=ciudad),
        Q(provincia__contains=provincia),
        Q(email__contains=email),
        Q(telefono__contains=telefono)
    )
    return render(request, 'compras/proveedores/index.html', {'page_obj': page_obj})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def importar_proveedores(request):
    template = "compras/proveedores/importar_proveedores.html"
    prompt = {
        'order': 'Orden del fichero CSV:  Nif, Nombre, Calle, Ciudad, Provincia, Codigo postal, Email, Telefono'
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
        Proveedor.objects.update_or_create(
            nif=column[0],
            nombre=column[1],
            calle=column[2],
            ciudad=column[3],
            provincia=column[4],
            codigo_postal=column[5],
            email=column[6],
            telefono=column[7]
        )
    return render(request, template)


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def exportar_proveedores(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Nif', 'Nombre', 'Calle', 'Ciudad', 'Provincia', 'Codigo postal', 'Email', 'Telefono'])
    for proveedor in Proveedor.objects.all().values_list(
            'nif', 'nombre', 'calle', 'ciudad', 'provincia', 'codigo_postal', 'email', 'telefono'):
        writer.writerow(proveedor)
    response['Content-Disposition'] = 'attachment; filename="proveedores.csv"'
    return response


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def compras_graficas(request):
    return render(request, 'compras/graficas/graficas.html', {'grafico_comercial_0': __generar_grafico_comercial(0),
                                                              'grafico_comercial_1': __generar_grafico_comercial(1),
                                                              'grafico_proveedor_0': __generar_grafico_proveedor(0),
                                                              'grafico_proveedor_1': __generar_grafico_proveedor(1)})


def __generar_grafico_comercial(opcion):
    comerciales = Empleado.objects.filter(Q(departamento__nombre='Comercial'))
    labels = list(c.nombre for c in comerciales)
    comercial_datos = {}
    extension = []
    for comercial in comerciales:
        if opcion == 0:
            total = comercial.calcular_gasto_total_por_comercial()
        else:
            total = comercial.calcular_numero_compras_por_comercial()
        comercial_datos[comercial] = total
    for value in comercial_datos.values():
        extension.append(value)
    x = np.arange(len(labels))
    width = 0.50
    fig, ax = plt.subplots()
    ax.tick_params(axis='x', rotation=70)
    ax.bar(x, extension, width)
    if opcion == 0:
        ax.set_title('Total gastado (€) por comercial')
    else:
        ax.set_title('Número de compras por comercial')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    fig.clear()
    return graphic


def __generar_grafico_proveedor(opcion):
    proveedores = Proveedor.objects.all()
    labels = list(p.nombre for p in proveedores)
    proveedor_datos = {}
    extension = []
    for proveedor in proveedores:
        if opcion == 0:
            total = proveedor.calcular_gasto_total_por_proveedor()
        else:
            total = proveedor.calcular_numero_compras_por_proveedor()
        proveedor_datos[proveedor] = total
    for value in proveedor_datos.values():
        extension.append(value)
    x = np.arange(len(labels))
    width = 0.50
    fig, ax = plt.subplots()
    ax.tick_params(axis='x', rotation=70)
    ax.bar(x, extension, width)
    if opcion == 0:
        ax.set_title('Total gastado (€) por proveedor')
    else:
        ax.set_title('Número de compras por proveedor')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    fig.clear()
    return graphic
