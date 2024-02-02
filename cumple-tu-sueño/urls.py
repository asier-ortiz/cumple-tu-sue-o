from django.conf.urls.static import static
from django.contrib import admin
from Empleados.views import *
from Inventario.views import *
from Ventas.views import *
from Compras.views import *
from django.urls import path, include
from django.contrib.auth import views

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', views.LoginView.as_view(), name='login'),
                  path('login/', views.LoginView.as_view(), name='login'),
                  path('login_redirect/', login_redirect, name='login_redirect'),
                  path('logout/', logout, name='logout'),
                  path('sin_autorizacion/', sin_autorizacion, name='sin_autorizacion'),

                  path('empleados/', empleados, name='empleados'),
                  path('empleados/crear_empleado/', crear_empleado, name='crear_empleado'),
                  path('empleados/modificar_empleado/<str:dni>', modificar_empleado, name='modificar_empleado'),
                  path('empleados/borrar_empleado/<str:dni>', borrar_empleado, name='borrar_empleado'),
                  path('empleados/buscar_empleado', buscar_empleado, name='buscar_empleado'),
                  path('empleados/importar_empleados', importar_empleados, name='importar_empleados'),
                  path('empleados/exportar_empleados', exportar_empleados, name='exportar_empleados'),
                  path('empleados/modificar_contraseña/<str:username>', modificar_contraseña,
                       name='modificar_contraseña'),

                  path('ventas/', ventas, name='ventas'),
                  path('ventas/crear_venta/', crear_venta, name='crear_venta'),
                  path('ventas/ver_detalle_venta/<str:id>', ver_detalle_venta, name='ver_detalle_venta'),
                  path('ventas/borrar_venta/<str:id>', borrar_venta, name='borrar_venta'),
                  path('ventas/generar_factura/<str:id>', generar_factura, name='generar_factura'),
                  path('ventas/graficas', ventas_graficas, name='ventas_graficas'),
                  path('clientes/', clientes, name='clientes'),
                  path('clientes/crear_cliente/', crear_cliente, name='crear_cliente'),
                  path('clientes/modificar_cliente/<str:nif>', modificar_cliente, name='modificar_cliente'),
                  path('clientes/borrar_cliente/<str:nif>', borrar_cliente, name='borrar_cliente'),
                  path('clientes/buscar_cliente', buscar_cliente, name='buscar_cliente'),
                  path('clientes/importar_clientes', importar_clientes, name='importar_clientes'),
                  path('clientes/exportar_clientes', exportar_clientes, name='exportar_clientes'),

                  path('compras/', compras, name='compras'),
                  path('compras/crear_compra/', crear_compra, name='crear_compra'),
                  path('compras/ver_detalle_compra/<str:id>', ver_detalle_compra, name='ver_detalle_compra'),
                  path('compras/borrar_compra/<str:id>', borrar_compra, name='borrar_compra'),
                  path('compras/graficas', compras_graficas, name='compras_graficas'),
                  path('proveedores/', proveedores, name='proveedores'),
                  path('proveedores/crear_proveedor/', crear_proveedor, name='crear_proveedor'),
                  path('proveedores/modificar_proveedor/<str:nif>', modificar_proveedor, name='modificar_proveedor'),
                  path('proveedores/borrar_proveedor/<str:nif>', borrar_proveedor, name='borrar_proveedor'),
                  path('proveedores/buscar_proveedor', buscar_proveedor, name='buscar_proveedor'),
                  path('proveedores/importar_proveedores', importar_proveedores, name='importar_proveedores'),
                  path('proveedores/exportar_proveedores', exportar_proveedores, name='exportar_proveedores'),

                  path('inventario/', productos, name='productos'),
                  path('inventario/crear_producto/', crear_producto, name='crear_producto'),
                  path('inventario/modificar_producto/<str:nombre>', modificar_producto, name='modificar_producto'),
                  path('inventario/borrar_producto/<str:nombre>', borrar_producto, name='borrar_producto'),
                  path('inventario/buscar_producto', buscar_producto, name='buscar_producto'),
                  path('inventario/importar_productos', importar_productos, name='importar_productos'),
                  path('inventario/exportar_productos', exportar_productos, name='exportar_productos'),

                  path('ckeditor/', include('ckeditor_uploader.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
