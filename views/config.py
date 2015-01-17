from models.models import *
NUMERO_DE_FACTURA_INICIAL = 2775

widgetTemplate = {'add':'addEntity.html', 'show':'showEntities.html'}

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
               'TipoEgreso':TipoEgreso}
keyDefs = {'Cliente':['nombre','negocio'],
           'Producto':['nombre'], 
           'Porcion':['valor','unidades'], 
           'GrupoDePrecios':['nombre'],
           'Precio':['producto','porcion','grupo'], 
           'Empleado':['nombre','apellido'], 
           'Factura':['numero'], 
           'Remision':['numero'],
           'Proveedor':['nombre'],
           'Bienoservicio':['nombre'],
           'PorcionCompra':['valor','unidades'],
           'TipoEgreso':['nombre']}

uiConfig = {'Cliente':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox', 'width':'10em'},
                       {'id':'negocio','ui':'Negocio', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                       {'id':'ciudad','ui':'Ciudad', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                       {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                       {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                       {'id':'nit','ui':'NIT', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                       {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                       {'id':'grupoDePrecios','ui':'Grupo de Precios', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}
                       ],
            'Producto':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'20em'}],
            'Porcion':[{'id':'valor','ui':'Porcion', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                       {'id':'unidades','ui':'Unidades', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}],
            'GrupoDePrecios':[{'id':'nombre', 'ui':'Nombre', 'required':'true','valid':'dijit/form/ValidationTextBox','width':'10em'}],
            'Precio':[{'id':'producto','ui':'Producto'},
                      {'id':'porcion','ui':'Porcion'},
                      {'id':'grupo','ui':'Grupo de Precios'},
                      {'id':'precio','ui':'Precio','required':'true','valid':'dijit/form/NumberTextBox','width':'10em'}
                      ],
            'Empleado':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'apellido', 'ui':'Apellido', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}],
            'Factura':[{'id':'numero', 'ui':'Numero'},
                       {'id':'empleado', 'ui':'Empleado'},
                       {'id':'cliente', 'ui':'Cliente'},
                       {'id':'fecha', 'ui':'Fecha'},
                       {'id':'total', 'ui':'Valor'}
                       ],
            'Remision':[{'id':'numero', 'ui':'Numero'},
                       {'id':'empleado', 'ui':'Empleado'},
                       {'id':'cliente', 'ui':'Cliente'},
                       {'id':'fecha', 'ui':'Fecha'},
                       {'id':'total', 'ui':'Valor'}],
            'Proveedor':[
                         {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox', 'width':'10em'},
                         {'id':'ciudad','ui':'Ciudad', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                         {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                         {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                         {'id':'nit','ui':'NIT', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                         {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                         {'id':'bienesoservicios','ui':'Bienes o Servicios'}
                         ],
            'Bienoservicio':[
                             {'id':'tipo', 'ui':'Tipo de Egreso'},
                             {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'20em'}
                      ],
            'PorcionCompra':[
                             {'id':'valor','ui':'Porcion', 'required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                             {'id':'unidades','ui':'Unidades', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}
                       ],
            'TipoEgreso':[
                          {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'20em'}
                          ],
            'Egreso':[
                      {'id':'numero','ui':'Numero','required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                      {'id':'tipo','ui':'Tipo','width':'10em'},
                      {'id':'detalle','ui':'Bien o Servicio','required':'true','valid':'','width':'10em'},
                      {'id':'total','ui':'Valor','required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                      {'id':'empleado','ui':'Empleado','width':'10em'}                      
                      ]
            }
createTemplateStings = {'Factura':'/crearFactura', 'Egreso':'/crearEgreso'}
templateNames = {'pivot':'pivot.html'}

