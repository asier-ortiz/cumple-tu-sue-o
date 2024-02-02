import csv
import io
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth import logout as do_logout
from Empleados.models import *
from .forms import EmpleadoForm, EmpleadoContraseñaForm


@login_required
@user_passes_test(lambda u: Group.objects.get(name='RRHH') in u.groups.all(), login_url='sin_autorizacion')
def empleados(request):
    empleados = Empleado.objects.order_by('nombre').filter(Q(activo=True))
    user = request.user
    empleado_logeado = get_object_or_404(Empleado, user=user)
    paginator = Paginator(empleados, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'empleados/index.html', {'page_obj': page_obj, 'empleado_logeado': empleado_logeado})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='RRHH') in u.groups.all(), login_url='sin_autorizacion')
def crear_empleado(request):
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.fotografia = request.FILES.get('fotografia')
            user = User.objects.create_user(
                username=new.nombre_usuario,
                password=new.contraseña,
                email=new.email
            )
            user.first_name = new.nombre
            user.last_name = new.apellidos
            departarmento = form.fields['departamento']

            if departarmento == 'RRHH':
                group = Group.objects.get(name='RRHH')
                group.user_set.add(user)
            elif departarmento == 'Comercial':
                group = Group.objects.get(name='Comercial')
                group.user_set.add(user)

            user.save()
            new.user = user
            form.save()
            return redirect('empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'empleados/crear_empleado.html', {'form': form})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='RRHH') in u.groups.all(), login_url='sin_autorizacion')
def modificar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    tree = empleado.generate_tree()
    tree_size = tree.size()
    form = EmpleadoForm(request.POST or None, instance=empleado)
    form.fields['dni'].widget.attrs['readonly'] = True
    form.fields['nombre_usuario'].widget.attrs['readonly'] = True
    form.fields['responsable'].queryset = Empleado.objects.exclude(dni__in=empleado.get_descendats_ids()).exclude(
        dni=empleado.dni)
    if form.is_valid():
        new = form.save(commit=False)
        if request.FILES.get('fotografia') is not None:
            new.fotografia = request.FILES.get('fotografia', default="/user.png")
        form.save()
        return redirect('empleados')
    return render(request, 'empleados/crear_empleado.html',
                  {'form': form, 'dni': empleado.dni, 'fotografia': empleado.fotografia, 'tree': tree,
                   'tree_size': tree_size})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='RRHH') in u.groups.all(), login_url='sin_autorizacion')
def borrar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    user = get_object_or_404(User, username=empleado.nombre_usuario)
    user.delete()
    return redirect('empleados')


@login_required
@user_passes_test(lambda u: Group.objects.get(name='RRHH') in u.groups.all(), login_url='sin_autorizacion')
def buscar_empleado(request):
    nombre = request.POST.get('nombre')
    apellidos = request.POST.get('apellidos')
    departamento = request.POST.get('departamento')
    activo = request.POST.get('activo')
    if departamento != 'Todos':
        page_obj = Empleado.objects.filter(
            Q(nombre__contains=nombre),
            Q(apellidos__contains=apellidos),
            Q(departamento__nombre__contains=departamento),
            Q(activo=activo)
        )
    else:
        page_obj = Empleado.objects.filter(
            Q(nombre__contains=nombre),
            Q(apellidos__contains=apellidos),
            Q(activo=activo)
        )
    return render(request, 'empleados/index.html', {'page_obj': page_obj})


@login_required
@user_passes_test(lambda u: Group.objects.get(name='RRHH') in u.groups.all(), login_url='sin_autorizacion')
def importar_empleados(request):
    template = "empleados/importar_empleados.html"
    prompt = {
        'order': 'Orden del fichero CSV: Nombre, Apellidos, Email, Teléfono, Departamento {nombre} ,'
                 'Responsable {dni}, Dni, Sexo, Estado civil, Fecha nacimiento {dd/mm/YYYY}, Nombre usuario, Contraseña, '
                 'Fecha contratación {dd/mm/YYYY}, Activo {true/false} '
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
        departamento = None
        try:
            departamento = Departamento.objects.get(nombre=column[4])
        except Departamento.DoesNotExist:
            departamento = None
        try:
            responsable = Empleado.objects.get(dni=column[5])
        except Empleado.DoesNotExist:
            responsable = None
        Empleado.objects.update_or_create(
            nombre=column[0],
            apellidos=column[1],
            email=column[2],
            telefono=column[3],
            departamento=departamento,
            responsable=responsable,
            dni=column[6],
            sexo=column[7],
            estado_civil=column[8],
            fecha_nacimiento=column[9],
            nombre_usuario=column[10],
            contraseña=column[11],
            fecha_contratacion=column[12],
            activo=column[13]
        )
        user = User.objects.create_user(
            username=column[10],
            password=column[11],
            email=column[2]
        )
        user.first_name = column[0]
        user.last_name = column[1]
        user.save()
        Empleado.objects.filter(dni=column[6]).update(user=user)
        if departamento.nombre == 'RRHH':
            group = Group.objects.get(name='RRHH')
            group.user_set.add(user)
        elif departamento.nombre == 'Comercial':
            group = Group.objects.get(name='Comercial')
            group.user_set.add(user)
    return render(request, template)


@login_required
@user_passes_test(lambda u: Group.objects.get(name='RRHH') in u.groups.all(), login_url='sin_autorizacion')
def exportar_empleados(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(
        ['Nombre', 'Apellidos', 'Email', 'Telefono', 'Departamento', 'Responsable', 'Dni', 'Sexo',
         'Estado civil', 'Fecha nacimiento', 'Nombre usuario', 'Contraseña', 'Fecha contratacion', 'Activo'])
    for empleado in Empleado.objects.all().values_list('nombre', 'apellidos', 'email', 'telefono',
                                                       'departamento__nombre', 'responsable', 'dni', 'sexo',
                                                       'estado_civil', 'fecha_nacimiento', 'nombre_usuario',
                                                       'contraseña', 'fecha_contratacion', 'activo'):
        writer.writerow(empleado)
    response['Content-Disposition'] = 'attachment; filename="empleados.csv"'
    return response


@login_required
def modificar_contraseña(request, username):
    user = get_object_or_404(User, username=username)
    empleado = get_object_or_404(Empleado, user=user)
    form = EmpleadoContraseñaForm(request.POST or None, instance=empleado)
    if form.is_valid():
        new = form.save(commit=False)
        user.set_password(new.contraseña)
        user.save()
        empleado.contraseña = new.contraseña
        form.save()
        return redirect('/')
    return render(request, 'empleados/modificar_contraseña.html', {'form': form})


def login_redirect(request):
    if has_group(request.user, 'RRHH'):
        return redirect('/empleados')
    elif has_group(request.user, 'Comercial'):
        return redirect('/ventas')
    else:
        return redirect('/')


def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@login_required
def logout(request):
    do_logout(request)
    return redirect('/')


@login_required
def sin_autorizacion(request):
    return render(request, 'registration/sin_autoriazacion.html')
