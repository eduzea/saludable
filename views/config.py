from models.models import *
NUMERO_DE_FACTURA_INICIAL = 2775

widgetTemplate = {'add':'addEntity.html', 'show':'showEntities.html'}


singletons = {'NumeroFactura':NumeroFactura,
              'NumeroRemision':NumeroRemision,
              'NumeroEgreso':NumeroEgreso,              
              'NumeroDeuda':NumeroDeuda
              }

classModels = {'Cliente':Cliente, 
               'Producto':Producto,
               'Porcion':Porcion, 
               'Precio':Precio, 
               'GrupoDePrecios':GrupoDePrecios, 
               'Factura':Factura, 
               'Remision':Remision ,
               'Empleado':Empleado, 
               'NumeroFactura':NumeroFactura, 
               'Venta':Venta,
               'Proveedor':Proveedor, 
               'Bienoservicio':Bienoservicio, 
               'PorcionCompra':PorcionCompra, 
               'Egreso':Egreso,
               'TipoEgreso':TipoEgreso,
               'TipoAcreedor':TipoAcreedor,
               'Sucursal':Sucursal,
               'Acreedor':Acreedor,
               'Deuda':Deuda}
keyDefs = {'Cliente':['nombre','negocio'],
           'Producto':['nombre'], 
           'Porcion':['valor','unidades'], 
           'GrupoDePrecios':['nombre'],
           'Precio':['producto','porcion','grupo'], 
           'Empleado':['nombre','apellido'],
           'Sucursal':['nombre'], 
           'Factura':['numero'], 
           'Remision':['numero'],
           'Proveedor':['nombre'],
           'Bienoservicio':['nombre'],
           'PorcionCompra':['valor','unidades'],
           'TipoEgreso':['nombre'],
           'TipoAcreedor':['nombre'],
           'Acreedor':['nombre'],
           'Deuda':['numero']}

uiConfig = {'Cliente':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox', 'width':'10em'},
                       {'id':'negocio','ui':'Negocio', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                       {'id':'ciudad','ui':'Ciudad', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'5em'},
                       {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'8em'},
                       {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'5em'},
                       {'id':'nit','ui':'NIT', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'6em'},
                       {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'4em'},
                       {'id':'grupoDePrecios','ui':'Grupo de Precios', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'5em'}
                       ],
            'Producto':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'20em'}],
            'Porcion':[{'id':'valor','ui':'Porcion', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                       {'id':'unidades','ui':'Unidades', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}],
            'GrupoDePrecios':[{'id':'nombre', 'ui':'Nombre', 'required':'true','valid':'dijit/form/ValidationTextBox','width':'10em'}],
            'Precio':[{'id':'producto','ui':'Producto', 'width':'20em'},
                      {'id':'porcion','ui':'Porcion','width':'5em'},
                      {'id':'grupo','ui':'Grupo de Precios','width':'8em'},
                      {'id':'precio','ui':'Precio','required':'true','valid':'dijit/form/NumberTextBox','width':'10em'}
                      ],
            'Empleado':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'apellido', 'ui':'Apellido', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}],
            'Sucursal':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'direccion', 'ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'telefono', 'ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}
                        ],
            'Factura':[{'id':'numero', 'ui':'Numero','width':'4em'},
                       {'id':'cliente', 'ui':'Cliente', 'width':'20em'},
                       {'id':'fecha', 'ui':'Fecha', 'width':'8em'},
                       {'id':'total', 'ui':'Valor', 'width':'8em'},
                       {'id':'empleado', 'ui':'Empleado', 'width':'8em'}
                       ],
            'Remision':[{'id':'numero', 'ui':'Numero','width':'4em'},
                       {'id':'empleado', 'ui':'Empleado','width':'8em'},
                       {'id':'cliente', 'ui':'Cliente', 'width':'20em'},
                       {'id':'fecha', 'ui':'Fecha','width':'8em'},
                       {'id':'total', 'ui':'Valor','width':'8em'}],
            'Proveedor':[
                         {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox', 'width':'10em'},
                         {'id':'ciudad','ui':'Ciudad', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'5em'},
                         {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                         {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'5em'},
                         {'id':'nit','ui':'NIT', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'8em'},
                         {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'5em'},
                         {'id':'bienesoservicios','ui':'Bienes o Servicios','width':'10em'}
                         ],
            'Bienoservicio':[
                             {'id':'tipo', 'ui':'Tipo de Egreso', 'width':'10em'},
                             {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'20em'}
                      ],
            'PorcionCompra':[
                             {'id':'valor','ui':'Porcion', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                             {'id':'unidades','ui':'Unidades', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}
                       ],
            'TipoEgreso':[
                          {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}
                          ],
            'Egreso':[
                      {'id':'numero','ui':'Numero','required':'true', 'valid':'dijit/form/NumberTextBox','width':'4em'},
                      {'id':'fecha', 'ui':'Fecha','width':'5em'},
                      {'id':'sucursal', 'ui':'Ciudad','width':'5em'},
                      {'id':'proveedor','ui':'Proveedor','width':'10em'},
                      {'id':'tipo','ui':'Tipo','width':'5em'},
                      {'id':'resumen','ui':'Bien o Servicio','required':'true','valid':'','width':'10em'},
                      {'id':'total','ui':'Valor','required':'true', 'valid':'dijit/form/NumberTextBox','width':'5em'},
                      {'id':'empleado','ui':'Empleado','width':'10em'}
                      ],
            'TipoAcreedor':[
                          {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}
                          ],
            'Acreedor':[
                        {'id':'tipo','ui':'Tipo','width':'10em'},
                        {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox', 'width':'10em'},
                        {'id':'nit','ui':'NIT', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'6em'},
                        {'id':'ciudad','ui':'Ciudad', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'5em'},
                        {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'8em'},
                        {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'5em'}
                        ],
            'Deuda':[
                     {'id':'numero','ui':'No.','required':'true', 'valid':'dijit/form/NumberTextBox','width':'2em'},
                     {'id':'fecha', 'ui':'Fecha','width':'5em','required':'true','valid':''},
                     {'id':'empleado','ui':'Empleado','width':'8em','required':'true','valid':'dijit/form/ValidationTextBox'},
                     {'id':'acreedor','ui':'Acreedor','width':'8em'},
                     {'id':'monto','ui':'Monto','required':'true', 'valid':'dijit/form/NumberTextBox','width':'5.5em'},
                     {'id':'interes','ui':'Interes(EA)','required':'true', 'valid':'dijit/form/NumberTextBox','width':'5em','default':'0'},
                     {'id':'vencimiento', 'ui':'Vencimiento','width':'5.5em','required':'true','valid':''},
                     {'id':'comentario', 'ui':'Comentario','required':'true','valid':'dijit/form/SimpleTextarea','width':'10em'},
                     {'id':'pagada', 'ui':'% Pagado','required':'true','valid':'dijit/form/NumberTextBox','width':'3em','default':'0'},
                     ]
            }
createTemplateStrings = {'Remision':'/crearFactura?entityClass=Remision','Factura':'/crearFactura?entityClass=Factura', 'Egreso':'/crearEgreso'}
templateNames = {'pivot':'pivot.html'}

