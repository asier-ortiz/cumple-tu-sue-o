import base64
import csv
import numpy as np
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from .utils import render_to_pdf
from Ventas.models import *
from .forms import ClienteForm
from django.contrib.auth.models import Group
from django.db.models import Q
import matplotlib.pyplot as plt
import io
import matplotlib
matplotlib.use('agg')


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def ventas(request):
    pedidos = Pedido.objects.order_by('-fecha')
    paginator = Paginator(pedidos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ventas/ventas/index.html', {'page_obj': page_obj})


@csrf_exempt
@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def crear_venta(request):
    productos = Producto.objects.all().filter(cantidad_disponible__gte=1)
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    clientes = Cliente.objects.order_by('nombre')
    if request.method == "POST":
        arr = request.POST.getlist('arr[]')
        cliente_pk = request.POST.get('cliente')
        if arr:
            diccionario = dict(zip(arr[::2], arr[1::2]))
            user = request.user
            comercial = get_object_or_404(Empleado, user=user)
            cliente = Cliente.objects.get(pk=cliente_pk)
            Pedido(cliente=cliente, comercial=comercial).save()
            pedido = Pedido.objects.last()
            for k, v in diccionario.items():
                producto = Producto.objects.get(pk=k)
                producto.actualizar_cantidad_restar(int(v))
                LineaPedido(pedido=pedido, producto=producto, cantidad=int(v)).save()
            return redirect('ventas')
    return render(request, 'ventas/ventas/crear_venta.html', {
        'page_obj': page_obj,
        'clientes': clientes})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def ver_detalle_venta(request, id):
    return render(request, 'ventas/ventas/detalle_venta.html', {'pedido': Pedido.objects.get(pk=id)})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def borrar_venta(request, id):
    pedido = Pedido.objects.get(pk=id)
    pedido.delete()
    return redirect('ventas')


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def generar_factura(request, id):
    context = {
        'pedido': Pedido.objects.get(pk=id),
    }
    pdf = render_to_pdf('ventas/ventas/factura.html', context)
    if pdf:
        return HttpResponse(pdf, content_type='aplication/pdf')
    return HttpResponse("Error: Factura no encontrada")


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def clientes(request):
    clientes = Cliente.objects.order_by('nombre')
    paginator = Paginator(clientes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ventas/clientes/index.html', {'page_obj': page_obj})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.imagen = request.FILES.get('imagen')
            form.save()
            return redirect('clientes')
    else:
        form = ClienteForm()
    return render(request, 'ventas/clientes/crear_cliente.html', {'form': form})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def modificar_cliente(request, nif):
    cliente = get_object_or_404(Cliente, nif=nif)
    form = ClienteForm(request.POST or None, instance=cliente)
    form.fields['nif'].widget.attrs['readonly'] = True
    if form.is_valid():
        new = form.save(commit=False)
        if request.FILES.get('imagen') is not None:
            new.imagen = request.FILES.get('imagen', default="/user.png")
        form.save()
        return redirect('clientes')
    return render(request, 'ventas/clientes/crear_cliente.html',
                  {'form': form, 'nif': cliente.nif, 'imagen': cliente.imagen})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def borrar_cliente(request, nif):
    cliente = get_object_or_404(Cliente, nif=nif)
    cliente.delete()
    return redirect('clientes')


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def buscar_cliente(request):
    nif = request.POST.get('nif')
    nombre = request.POST.get('nombre')
    ciudad = request.POST.get('ciudad')
    provincia = request.POST.get('provincia')
    email = request.POST.get('email')
    telefono = request.POST.get('telefono')
    page_obj = Cliente.objects.filter(
        Q(nif__contains=nif),
        Q(nombre__contains=nombre),
        Q(ciudad__contains=ciudad),
        Q(provincia__contains=provincia),
        Q(email__contains=email),
        Q(telefono__contains=telefono)
    )
    return render(request, 'ventas/clientes/index.html', {'page_obj': page_obj})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def importar_clientes(request):
    template = "ventas/clientes/importar_clientes.html"
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
        Cliente.objects.update_or_create(
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
def exportar_clientes(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Nif', 'Nombre', 'Calle', 'Ciudad', 'Provincia', 'Codigo postal', 'Email', 'Telefono'])
    for cliente in Cliente.objects.all().values_list(
            'nif', 'nombre', 'calle', 'ciudad', 'provincia', 'codigo_postal', 'email', 'telefono'):
        writer.writerow(cliente)
    response['Content-Disposition'] = 'attachment; filename="clientes.csv"'
    return response


@login_required
@user_passes_test(lambda u: Group.objects.get(name='Comercial') in u.groups.all(), login_url='sin_autorizacion')
def ventas_graficas(request):
    return render(request, 'ventas/graficas/graficas.html', {'grafico_comercial_0': __generar_grafico_comercial(0),
                                                             'grafico_comercial_1': __generar_grafico_comercial(1),
                                                             'grafico_cliente_0': __generar_grafico_cliente(0),
                                                             'grafico_cliente_1': __generar_grafico_cliente(1)})


def __generar_grafico_comercial(opcion):
    comerciales = Empleado.objects.filter(Q(departamento__nombre='Comercial'))
    labels = list(c.nombre for c in comerciales)
    comercial_datos = {}
    extension = []
    for comercial in comerciales:
        if opcion == 0:
            total = comercial.calcular_recaudacion_total_por_comercial()
        else:
            total = comercial.calcular_numero_ventas_por_comercial()
        comercial_datos[comercial] = total
    for value in comercial_datos.values():
        extension.append(value)
    x = np.arange(len(labels))
    width = 0.50
    fig, ax = plt.subplots()
    ax.tick_params(axis='x', rotation=70)
    ax.bar(x, extension, width)
    if opcion == 0:
        ax.set_title('Total recaudado (€) por comercial')
    else:
        ax.set_title('Número de ventas por comercial')
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


def __generar_grafico_cliente(opcion):
    clientes = Cliente.objects.all()
    labels = list(c.nombre for c in clientes)
    cliente_datos = {}
    extension = []
    for cliente in clientes:
        if opcion == 0:
            total = cliente.calcular_gasto_total_por_cliente()
        else:
            total = cliente.calcular_numero_compras_por_cliente()
        cliente_datos[cliente] = total
    for value in cliente_datos.values():
        extension.append(value)
    x = np.arange(len(labels))
    width = 0.50
    fig, ax = plt.subplots()
    ax.tick_params(axis='x', rotation=70)
    ax.bar(x, extension, width)
    if opcion == 0:
        ax.set_title('Total gastado (€) por cliente')
    else:
        ax.set_title('Número de compras por cliente')
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
