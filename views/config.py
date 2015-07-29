from models.models import *
NUMERO_DE_FACTURA_INICIAL = 2775

widgetTemplate = {'add':'addEntity.html', 'show':'showEntities.html'}


singletons = {'NumeroFactura':NumeroFactura,
              'NumeroRemision':NumeroRemision,
              'NumeroEgreso':NumeroEgreso,              
              'NumeroDeuda':NumeroDeuda,
              'NumeroOtrosIngresos':NumeroOtrosIngresos,
              'NumeroActivoFijo':NumeroActivoFijo,
              'NumeroPagoRecibido':NumeroPagoRecibido,
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
               'Clase':Clase,
               'Grupo':Grupo,
               'Cuenta':Cuenta,
               'SubCuenta':SubCuenta, 
               'PorcionCompra':PorcionCompra, 
               'Egreso':Egreso,
               'Compra':Compra,
               'TipoEgreso':TipoEgreso,
               'TipoAcreedor':TipoAcreedor,
               'Sucursal':Sucursal,
               'Ciudad':Ciudad,
               'Acreedor':Acreedor,
               'Deuda':Deuda,
               'Devolucion':Devolucion,
               'OtrosIngresos':OtrosIngresos,
               'CapitalSocial':CapitalSocial,
               'CapitalPagado':CapitalPagado,
               'ActivoFijo':ActivoFijo,
               'CuentaBancaria':CuentaBancaria,
               'Banco':Banco,
               'TipoDeCuenta':TipoDeCuenta,
               'SaldoCuentaBancaria':SaldoCuentaBancaria,
               'CuentaPorCobrar':CuentaPorCobrar,
               'MedioDePago':MedioDePago,
               'CuentaTransferencias':CuentaTransferencias,
               'PagoRecibido':PagoRecibido,
               'InventarioRegistro':InventarioRegistro,
               'Inventario':Inventario}
keyDefs = {'Cliente':['nombre','negocio'],
           'Producto':['nombre'], 
           'Porcion':['valor','unidades'], 
           'GrupoDePrecios':['nombre'],
           'Precio':['producto','porcion','grupoDePrecios'], 
           'Empleado':['nombre','apellido'],
           'Sucursal':['nombre'],
           'Ciudad':['nombre'], 
           'Factura':['numero'],
           'Venta':['producto','porcion'],
           'Egreso':['numero'],
           'Compra':['bienoservicio'], 
           'Remision':['numero'],
           'Proveedor':['nombre'],
           'Bienoservicio':['nombre'],
           'PorcionCompra':['valor','unidades'],
           'TipoEgreso':['nombre'],
           'TipoAcreedor':['nombre'],
           'Acreedor':['nombre'],
           'Deuda':['numero'],
           'Clase':['pucNumber'],
           'Grupo':['pucNumber'],
           'Cuenta':['pucNumber'],
           'SubCuenta':['pucNumber'],
           'OtrosIngresos':['numero'],
           'CapitalSocial':['socio'],
           'CapitalPagado':['fecha'],
           'ActivoFijo':['numero'],
           'CuentaBancaria':['numero'],
           'Banco':['nombre'],
           'TipoDeCuenta':['nombre'],
           'SaldoCuentaBancaria':['fecha'],
           'CuentaPorCobrar':['cliente'],
           'MedioDePago':['nombre'],
           'CuentaTransferencias':['numero'],
           'PagoRecibido':['numero'],
           'InventarioRegistro':['numero'],
           'Inventario':['fecha']
           }

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
                      {'id':'grupoDePrecios','ui':'Grupo de Precios','width':'8em'},
                      {'id':'precio','ui':'Precio','required':'true','valid':'dijit/form/NumberTextBox','width':'10em'}
                      ],
            'Empleado':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'apellido', 'ui':'Apellido', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'email', 'ui':'Email', 'required':'true', 'valid':'dijit/form/ValidationTextBox','dojoprops':'validator:dojox.validate.isEmailAddress','width':'10em'}
                        ],
            'Sucursal':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'direccion', 'ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        {'id':'telefono', 'ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'}
                        ],
            'Ciudad':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                        ],
            'Factura':[{'id':'numero', 'ui':'Numero','width':'4em'},
                       {'id':'cliente', 'ui':'Cliente', 'width':'20em'},
                       {'id':'fecha', 'ui':'Fecha', 'width':'8em'},
                       {'id':'total', 'ui':'Valor', 'width':'8em'},
                       {'id':'empleado', 'ui':'Empleado', 'width':'10em'},
                       {'id':'pagada', 'ui':'Pagada', 'width':'4em'},
                       {'id':'pagoRef', 'ui':'Ref. Pago', 'width':'4em'},
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
                             {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                             {'id':'clase','ui':'Clase', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                             {'id':'grupo','ui':'Grupo', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                             {'id':'cuenta','ui':'Cuenta', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                             {'id':'subcuenta','ui':'Subcuenta', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      ],
            'Clase':[
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      ],
            'Grupo':[
                      {'id':'clase','ui':'Clase', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                                            
                      ],
            'Cuenta':[
                      {'id':'grupo','ui':'Grupo', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      ],
            'SubCuenta':[
                      {'id':'cuenta','ui':'Cuenta', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},   
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
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
                     {'id':'montoPagado', 'ui':'Monto Pagado','required':'true','valid':'dijit/form/NumberTextBox','width':'5.5em','default':'0'},
#                      {'id':'pagada', 'ui':'% Pagado','required':'true','valid':'dijit/form/NumberTextBox','width':'3em','default':'0'},
                     ],
            'OtrosIngresos':[
                             {'id':'numero','ui':'No.','required':'true', 'valid':'dijit/form/NumberTextBox','width':'2em'},
                             {'id':'empleado','ui':'Empleado','width':'8em'},
                             {'id':'fecha', 'ui':'Fecha','width':'5em','required':'true','valid':''},
                             {'id':'descripcion', 'ui':'Descripcion','required':'true','valid':'dijit/form/SimpleTextarea','width':'10em'},
                             {'id':'total','ui':'Monto','required':'true','valid':'dijit/form/NumberTextBox','width':'10em'}
                             ],
            'CapitalSocial':[
                             {'id':'socio','ui':'Socio', 'required':'true', 'valid':'dijit/form/ValidationTextBox', 'width':'10em'},
                             {'id':'acciones','ui':'No. Acciones','required':'true','valid':'dijit/form/NumberTextBox','width':'10em'},
                             {'id':'total','ui':'Valor','required':'true','valid':'dijit/form/NumberTextBox','width':'10em'},
                             {'id':'participacion', 'ui':'Participacion (%)','required':'true','valid':'','width':'8em', 'disabled':True}
                             ],
            'CapitalPagado':[
                             {'id':'fecha', 'ui':'Fecha','width':'5em','required':'true','valid':''},
                             {'id':'valor','ui':'Valor','required':'true','valid':'dijit/form/NumberTextBox','width':'10em'},
                             ],
            'ActivoFijo':[
                      {'id':'numero','ui':'No.','required':'true', 'valid':'dijit/form/NumberTextBox','width':'2em'},
                      {'id':'fechaDeAdquisicion', 'ui':'Fecha de compra','width':'5em','required':'true','valid':''},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                      {'id':'grupo','ui':'Grupo', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'8em'},
                      {'id':'cuenta','ui':'Cuenta', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'8em'},
                      {'id':'subcuenta','ui':'Subcuenta', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'8em'},
                      {'id':'valorPagado','ui':'Valor Pagado','required':'true','valid':'dijit/form/NumberTextBox','width':'8em'},
                      {'id':'valorActual','ui':'Valor Actual','required':'true','valid':'dijit/form/NumberTextBox','width':'8em'},
                      ],
            'CuentaBancaria':[
                              {'id':'banco','ui':'Banco','width':'10em'},
                              {'id':'tipo','ui':'Tipo de Cuenta','width':'5em'},
                              {'id':'numero','ui':'No.','required':'true', 'valid':'dijit/form/NumberTextBox','width':'10em'},
                              {'id':'titular','ui':'Titular', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                              ],
            'Banco':[
                     {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                     {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                     {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                     {'id':'contacto','ui':'Contacto', 'required':'false', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                     ],
            'TipoDeCuenta':[
                            {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                            ],
            'SaldoCuentaBancaria':[
                                   {'id':'cuenta','ui':'Cuenta','width':'10em'},
                                   {'id':'fecha', 'ui':'Fecha','width':'5em'},
                                   {'id':'saldo', 'ui':'Saldo','width':'5em','required':'true','valid':'dijit/form/NumberTextBox'},
                                   ],
            'MedioDePago':[
                           {'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                           ],
            'CuentaTransferencias':[
                           {'id':'numero','ui':'No.','required':'true', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                           {'id':'cliente','ui':'Cliente','width':'15em'},
                           ],
            'PagoRecibido':[
                              {'id':'numero','ui':'No.','required':'true', 'valid':'dijit/form/NumberTextBox','width':'2em'},
                              {'id':'fecha', 'ui':'Fecha','width':'5em','required':'true','valid':''},
                              {'id':'cliente','ui':'Cliente','width':'15em'},
                              {'id':'medio','ui':'Medio de pago','width':'8em'},
                              {'id':'documento','ui':'Documento','required':'false', 'valid':'dijit/form/ValidationTextBox','width':'10em'},
                              {'id':'monto','ui':'Monto','required':'true', 'valid':'dijit/form/NumberTextBox','width':'5em'},
                              ],
            'InventarioRegistro':[
                                  {'id':'numero','ui':'No.','required':'true', 'valid':'dijit/form/NumberTextBox','width':'2em'},
                                  {'id':'fecha', 'ui':'Fecha','width':'5em','required':'true','valid':''},
                                  {'id':'ciudad','ui':'Ciudad','width':'5em'},
                                  {'id':'producto','ui':'Producto','width':'10em'},
                                  {'id':'porcion','ui':'Porcion','width':'5em'},
                                  {'id':'existencias','ui':'Existencias','required':'true', 'valid':'dijit/form/NumberTextBox','width':'5em'},
                                  ],
            'Inventario':[
                          {'id':'ciudad','ui':'Ciudad','width':'5em'},
                          {'id':'fecha', 'ui':'Fecha','width':'5em','required':'true','valid':''}
                          ]
            }

templateStrings = {'Remision':'/crearFactura?entityClass=Remision',
                   'Factura':'/crearFactura?entityClass=Factura', 
                   'Egreso':'/crearEgreso',
                   'Inventario':'/dojoxLoader?entityClass=Inventario&template=crearInventario.html',
#                    'Inventario':'/crearInventario.html',
                   'tablaDinamica':'/tablaDinamica.html',
                   'numeros':'/numeros.html',
                   'pYg':'/pYg.html',
                   'CuentasPorCobrar':'cuentasPorCobrar.html',
                   'Existencias':'existencias.html'
                   }
detailFields = {
               'Factura':'ventas',
               'Remision':'ventas',
               'Egreso':'compras',
               'Inventario':'registros'
               }


