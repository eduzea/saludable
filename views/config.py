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
               'Fruta':Fruta,
               'LoteDeCompra':LoteDeCompra,
               'LoteDeCompra':LoteDeCompra,
               'Clase':Clase,
               'Grupo':Grupo,
               'Cuenta':Cuenta,
               'SubCuenta':SubCuenta, 
               'PorcionCompra':PorcionCompra, 
               'Egreso':Egreso,
               'Fuente':Fuente,
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
               'Inventario':Inventario,
               'Existencias':Existencias,
               'ExistenciasRegistro':ExistenciasRegistro,
               'Produccion':Produccion,
               'ProductoPorcion':ProductoPorcion,
               'Fuente':Fuente}
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
           'LoteDeCompra':['fecha','fruta','proveedor'],
           'Compra':['bienoservicio'], 
           'Remision':['numero'],
           'Proveedor':['nombre'],
           'Bienoservicio':['nombre'],
           'Fruta':['nombre'],
           'LoteDeCompra':['fruta','proveedor','fecha'],
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
           'Inventario':['fecha','sucursal'],
           'InventarioRegistro':['fecha','sucursal','producto','porcion'],
           'Existencias':['fecha','sucursal'],
           'ExistenciasRegistro':['sucursal','producto','porcion'],
           'Produccion':['fecha','sucursal','fruta'],
           'ProductoPorcion':['porcion'],
           'Fuente':['nombre']
           }

uiConfigAdd = {'Cliente':[{'id':'nombre','ui':'Nombre', 'required':'true','style':'width:10em'},
                       {'id':'negocio','ui':'Negocio', 'required':'true', 'style':'width:10em'},
                       {'id':'ciudad','ui':'Ciudad', 'required':'true', 'style':'width:5em'},
                       {'id':'sucursal','ui':'Provee', 'required':'true', 'style':'width:5em'},
                       {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:8em'},
                       {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:5em'},
                       {'id':'nit','ui':'NIT', 'required':'true', 'style':'width:6em'},
                       {'id':'diasPago','ui':'Dias para pago', 'required':'true','style':'width:4em'},
                       {'id':'grupoDePrecios','ui':'Grupo de Precios', 'required':'true', 'style':'width:5em'},
                       {'id':'activo', 'ui':'Activo', 'required':'true', 'style':''}
                       ],
            'Producto':[{'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:20em'},
                        {'id':'activo', 'ui':'Activo', 'required':'true', 'style':''}],
            'Porcion':[{'id':'valor','ui':'Porcion', 'required':'true', 'style':'width:10em'},
                       {'id':'unidades','ui':'Unidades', 'required':'true', 'style':'width:10em'}],
            'GrupoDePrecios':[{'id':'nombre', 'ui':'Nombre', 'required':'true','style':'width:10em'}],
            'Precio':[{'id':'producto','ui':'Producto', 'style':'width:20em'},
                      {'id':'porcion','ui':'Porcion','style':'width:5em'},
                      {'id':'grupoDePrecios','ui':'Grupo de Precios','style':'width:8em'},
                      {'id':'precio','ui':'Precio','required':'true','style':'width:10em'}
                      ],
            'Empleado':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'style':'width:10em'},
                        {'id':'apellido', 'ui':'Apellido', 'required':'true', 'style':'width:10em'},
                        {'id':'email', 'ui':'Email', 'required':'true', 'dojoprops':'validator:dojox.validate.isEmailAddress','style':'width:10em'},
                        {'id':'activo', 'ui':'Activo', 'required':'true', 'style':''},
                        ],
            'Sucursal':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'style':'width:10em'},
                        {'id':'direccion', 'ui':'Direccion', 'required':'true', 'style':'width:10em'},
                        {'id':'telefono', 'ui':'Telefono', 'required':'true', 'style':'width:10em'}
                        ],
            'Ciudad':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'style':'width:10em'},
                        ],
            'Factura':[{'id':'numero', 'ui':'Numero','style':'width:4em'},
                       {'id':'cliente', 'ui':'Cliente', 'style':'width:20em'},
                       {'id':'fecha', 'ui':'Fecha', 'style':'width:5em'},
                       {'id':'total', 'ui':'Valor', 'style':'width:5em'},
                       {'id':'empleado', 'ui':'Empleado', 'style':'width:8em'},
                       {'id':'fechaVencimiento', 'ui':'Vence', 'style':'width:8em'},
                       {'id':'pagada', 'ui':'Pagada', 'style':'width:3em'},
                       {'id':'pagoRef', 'ui':'Ref. Pago', 'style':'width:4em'},
                       ],
            'Remision':[{'id':'numero', 'ui':'Numero','style':'width:4em'},
                       {'id':'empleado', 'ui':'Empleado','style':'width:8em'},
                       {'id':'cliente', 'ui':'Cliente', 'style':'width:20em'},
                       {'id':'fecha', 'ui':'Fecha','style':'width:5em'},
                       {'id':'total', 'ui':'Valor','style':'width:5em'},
                       {'id':'factura', 'ui':'Factura', 'style':'width:5em'}],
            'Proveedor':[
                         {'id':'nombre','ui':'Nombre', 'required':'true',  'style':'width:15em'},
                         {'id':'ciudad','ui':'Ciudad', 'required':'true', 'style':'width:5em'},
                         {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:10em'},
                         {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:5em'},
                         {'id':'nit','ui':'NIT', 'required':'true', 'style':'width:8em'},
                         {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'style':'width:5em'},
                         {'id':'bienesoservicios','ui':'Bienes o Servicios','style':'width:10em'},
                        {'id':'activo', 'ui':'Activo', 'required':'true', 'style':''}
                         ],
            'Bienoservicio':[
                             {'id':'tipo', 'ui':'Tipo de Egreso', 'style':'width:10em'},
                             {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                             {'id':'clase','ui':'Clase', 'required':'true', 'style':'width:10em'},
                             {'id':'grupo','ui':'Grupo', 'required':'true', 'style':'width:10em'},
                             {'id':'cuenta','ui':'Cuenta', 'required':'true', 'style':'width:10em'},
                             {'id':'subcuenta','ui':'Subcuenta', 'required':'true', 'style':'width:10em'},
                      ],
            'Fruta':[
                     {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                    ],
            'Clase':[
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                      ],
            'Grupo':[
                      {'id':'clase','ui':'Clase', 'required':'true', 'style':'width:10em'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                                            
                      ],
            'Cuenta':[
                      {'id':'grupo','ui':'Grupo', 'required':'true', 'style':'width:10em'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                      ],
            'SubCuenta':[
                      {'id':'cuenta','ui':'Cuenta', 'required':'true', 'style':'width:10em'},   
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                      ],
            'PorcionCompra':[
                             {'id':'valor','ui':'Porcion', 'required':'true', 'style':'width:10em'},
                             {'id':'unidades','ui':'Unidades', 'required':'true', 'style':'width:10em'}
                       ],
            'TipoEgreso':[
                          {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                          ],
            'Egreso':[
                      {'id':'numero','ui':'Numero','required':'true', 'style':'width:4em'},
                      {'id':'fecha', 'ui':'Fecha','style':'width:5em'},
                      {'id':'sucursal', 'ui':'Ciudad','style':'width:5em'},
                      {'id':'proveedor','ui':'Proveedor','style':'width:10em'},
                      {'id':'tipo','ui':'Tipo','style':'width:5em'},
                      {'id':'resumen','ui':'Bien o Servicio','required':'true','style':'width:10em'},
                      {'id':'total','ui':'Valor','required':'true', 'style':'width:5em'},
                      {'id':'empleado','ui':'Empleado','style':'width:10em'}
                      ],
            'TipoAcreedor':[
                          {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                          ],
            'LoteDeCompra':[
                            {'id':'fecha','ui':'Fecha', 'required':'true', 'style':'width:10em'},
                            {'id':'fruta','ui':'Fruta', 'required':'true', 'style':'width:10em'},
                            {'id':'proveedor','ui':'Proveedor', 'required':'true', 'style':'width:10em'},
                            {'id':'precio','ui':'Precio($/kg)', 'required':'true', 'style':'width:10em'},
                            {'id':'peso','ui':'Peso(kg)', 'required':'true', 'style':'width:10em'},
                            {'id':'procesado','ui':'Procesado', 'required':'true', 'style':''},
                            ],
            'Acreedor':[
                        {'id':'tipo','ui':'Tipo','style':'width:10em'},
                        {'id':'nombre','ui':'Nombre', 'required':'true',  'style':'width:10em'},
                        {'id':'nit','ui':'NIT', 'required':'true', 'style':'width:6em'},
                        {'id':'ciudad','ui':'Ciudad', 'required':'true', 'style':'width:5em'},
                        {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:8em'},
                        {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:5em'}
                        ],
            'Deuda':[
                     {'id':'numero','ui':'No.','readonly':'true','style':'width:2em','auto':''},
                     {'id':'fecha', 'ui':'Fecha','style':'width:7em'},
                     {'id':'empleado','ui':'Empleado','style':'width:8em'},
                     {'id':'acreedor','ui':'Acreedor','style':'width:8em'},
                     {'id':'monto','ui':'Monto','required':'true', 'style':'width:5em'},
                     {'id':'interes','ui':'Interes(EA)','required':'true', 'style':'width:5em','default':'0'},
                     {'id':'vencimiento', 'ui':'Vencimiento','style':'width:7em'},
                     {'id':'montoPagado', 'ui':'Monto Pagado','required':'true','style':'width: 5em','default':'0'},
                     {'id':'comentario', 'ui':'Comentario','required':'true','style':'width:10em;'},
#                      {'id':'pagada', 'ui':'% Pagado','required':'true','style':'width:3em','default':'0'},
                     ],
            'OtrosIngresos':[
                             {'id':'numero','ui':'No.','required':'true', 'readonly':'true','auto':'','style':'width:2em'},
                             {'id':'empleado','ui':'Empleado','style':'width:8em'},
                             {'id':'fecha', 'ui':'Fecha','style':'width:5em','required':'true'},
                             {'id':'descripcion', 'ui':'Descripcion','required':'true','style':'width:10em'},
                             {'id':'total','ui':'Monto','required':'true','style':'width:10em'}
                             ],
            'CapitalSocial':[
                             {'id':'socio','ui':'Socio', 'required':'true',  'style':'width:10em'},
                             {'id':'acciones','ui':'No. Acciones','required':'true','style':'width:10em'},
                             {'id':'total','ui':'Valor','required':'true','style':'width:10em'},
                             {'id':'participacion', 'ui':'Participacion (%)','required':'true','style':'width:8em', 'disabled':'true'}
                             ],
            'CapitalPagado':[
                             {'id':'fecha', 'ui':'Fecha','style':'width:10em','required':'true'},
                             {'id':'valor','ui':'Valor','required':'true','style':'width:10em'},
                             ],
            'ActivoFijo':[
                      {'id':'numero','ui':'No.','required':'true', 'style':'width:2em', 'readonly':'true', 'auto':'true'},
                      {'id':'fechaDeAdquisicion', 'ui':'Fecha de compra','style':'width:10em','required':'true'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'grupo','ui':'Grupo', 'required':'true', 'style':'width:8em'},
                      {'id':'cuenta','ui':'Cuenta', 'required':'true', 'style':'width:8em'},
                      {'id':'subcuenta','ui':'Subcuenta', 'required':'true', 'style':'width:8em'},
                      {'id':'valorPagado','ui':'Valor Pagado','required':'true','style':'width:8em'},
                      {'id':'valorActual','ui':'Valor Actual','required':'true','style':'width:8em'},
                      ],
            'CuentaBancaria':[
                              {'id':'banco','ui':'Banco','style':'width:10em'},
                              {'id':'tipo','ui':'Tipo de Cuenta','style':'width:5em'},
                              {'id':'numero','ui':'No.','required':'true', 'style':'width:10em'},
                              {'id':'titular','ui':'Titular', 'required':'true', 'style':'width:10em'},
                              ],
            'Banco':[
                     {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                     {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:10em'},
                     {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:10em'},
                     {'id':'contacto','ui':'Contacto', 'required':'false', 'style':'width:10em'},
                     ],
            'TipoDeCuenta':[
                            {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                            ],
            'SaldoCuentaBancaria':[
                                   {'id':'cuenta','ui':'Cuenta','style':'width:10em'},
                                   {'id':'fecha', 'ui':'Fecha','style':'width:7em'},
                                   {'id':'saldo', 'ui':'Saldo','style':'width:5em','required':'true','valid':'dijit/form/NumberTextBox'},
                                   ],
            'MedioDePago':[
                           {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                           ],
            'CuentaTransferencias':[
                           {'id':'numero','ui':'No.','required':'true', 'style':'width:10em'},
                           {'id':'cliente','ui':'Cliente','style':'width:15em'},
                           ],
            'PagoRecibido':[
                              {'id':'numero','ui':'No.','required':'true', 'style':'width:2em','readonly':'true','auto':''},
                              {'id':'fecha', 'ui':'Fecha','style':'width:8em','required':'true'},
                              {'id':'cliente','ui':'Cliente','style':'width:15em'},
                              {'id':'medio','ui':'Medio de pago','style':'width:8em'},
                              {'id':'oficina','ui':'Oficina','style':'width:8em'},
                              {'id':'documento','ui':'Documento','required':'false', 'style':'width:10em'},
                              {'id':'monto','ui':'Monto','required':'true', 'style':'width:5em'},
                              {'id':'facturas','ui':'Facturas','required':'true', 'style':'width:5em'}
                              ],
            'Inventario':[
                          {'id':'sucursal','ui':'Sucursal','style':'width:5em'},
                          {'id':'fecha', 'ui':'Fecha','style':'width:5em','required':'true'},
                          ],
            'Produccion':[
                          {'id':'fecha', 'ui':'Fecha','style':'width:8em'},
                          {'id':'sucursal','ui':'Sucursal','style':'width:5em'},
                          {'id':'fruta','ui':'Fruta', 'style':'width:10em'},
                          {'id':'loteDeCompra','ui':'Lote de Compra', 'style':'width:10em'},
                          {'id':'pesoFruta','ui':'Peso Fruta (kg)','required':'true', 'style':'width:5em'},                          
                          {'id':'productos','ui':'Productos','style':'width:10em'},
                          {'id':'rendimiento','ui':'Rendimiento (%)','required':'false', 'style':'width:3em'},
                          {'id':'costoBruto','ui':'Costo Bruto ($/kg)','required':'false', 'style':'width:5em'}
                          ],
            'ProductoPorcion':[
                               {'id':'porcion','ui':'Porcion','style':'width:5em'},
                               {'id':'cantidad','ui':'Cantidad','style':'width:5em', 'required':'true', 'default':0}
                            ],
            'Fuente':[
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                    ],
            }

uiConfigShow = {'Cliente':[{'id':'nombre','ui':'Nombre', 'required':'true','style':'width:10em'},
                       {'id':'negocio','ui':'Negocio', 'required':'true', 'style':'width:8em'},
                       {'id':'ciudad','ui':'Ciudad', 'required':'true', 'style':'width:5em'},
                       {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:8em'},
                       {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:5em'},
                       {'id':'nit','ui':'NIT', 'required':'true', 'style':'width:6em'},
                       {'id':'diasPago','ui':'Dias para pago', 'required':'true','style':'width:3em'},
                       {'id':'grupoDePrecios','ui':'Grupo de Precios', 'required':'true', 'style':'width:5em'},
                       {'id':'activo', 'ui':'Activo', 'required':'true', 'style':'width:3em'}
                       ],
            'Producto':[{'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:20em'},
                        {'id':'activo', 'ui':'Activo', 'required':'true', 'style':'width:3em'}
                        ],
            'Porcion':[{'id':'valor','ui':'Porcion', 'required':'true', 'style':'width:10em'},
                       {'id':'unidades','ui':'Unidades', 'required':'true', 'style':'width:10em'}],
            'GrupoDePrecios':[{'id':'nombre', 'ui':'Nombre', 'required':'true','style':'width:10em'}],
            'Precio':[{'id':'producto','ui':'Producto', 'style':'width:20em'},
                      {'id':'porcion','ui':'Porcion','style':'width:5em'},
                      {'id':'grupoDePrecios','ui':'Grupo de Precios','style':'width:8em'},
                      {'id':'precio','ui':'Precio','required':'true','style':'width:10em'}
                      ],
            'Empleado':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'style':'width:10em'},
                        {'id':'apellido', 'ui':'Apellido', 'required':'true', 'style':'width:10em'},
                        {'id':'email', 'ui':'Email', 'required':'true', 'dojoprops':'validator:dojox.validate.isEmailAddress','style':'width:10em'},
                        {'id':'activo', 'ui':'Activo', 'required':'true', 'style':'width:3em'},
                        ],
            'Sucursal':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'style':'width:10em'},
                        {'id':'direccion', 'ui':'Direccion', 'required':'true', 'style':'width:10em'},
                        {'id':'telefono', 'ui':'Telefono', 'required':'true', 'style':'width:10em'}
                        ],
            'Ciudad':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'style':'width:10em'},
                        ],
            'Factura':[{'id':'numero', 'ui':'Numero','style':'width:4em'},
                       {'id':'cliente', 'ui':'Cliente', 'style':'width:20em'},
                       {'id':'fecha', 'ui':'Fecha', 'style':'width:5em'},
                       {'id':'total', 'ui':'Valor', 'style':'width:5em'},
                       {'id':'empleado', 'ui':'Empleado', 'style':'width:8em'},
                       {'id':'fechaVencimiento', 'ui':'Vence', 'style':'width:5em', 'type':'Date'}
                       ],
            'Remision':[{'id':'numero', 'ui':'Numero','style':'width:4em'},
                       {'id':'empleado', 'ui':'Empleado','style':'width:8em'},
                       {'id':'cliente', 'ui':'Cliente', 'style':'width:20em'},
                       {'id':'fecha', 'ui':'Fecha','style':'width:5em'},
                       {'id':'total', 'ui':'Valor','style':'width:5em'},
                       {'id':'factura', 'ui':'Factura', 'style':'width:5em'}],
            'Proveedor':[
                         {'id':'nombre','ui':'Nombre', 'required':'true',  'style':'width:10em'},
                         {'id':'ciudad','ui':'Ciudad', 'required':'true', 'style':'width:4em'},
                         {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:8em'},
                         {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:4em'},
                         {'id':'nit','ui':'NIT', 'required':'true', 'style':'width:5em'},
                         {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'style':'width:4em'},
                         {'id':'bienesoservicios','ui':'Bienes o Servicios','style':'width:10em'},
                         {'id':'activo', 'ui':'Activo', 'required':'true', 'style':'width:3em'}
                         ],
            'Bienoservicio':[
                             {'id':'tipo', 'ui':'Tipo de Egreso', 'style':'width:10em'},
                             {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                             {'id':'clase','ui':'Clase', 'required':'true', 'style':'width:10em'},
                             {'id':'grupo','ui':'Grupo', 'required':'true', 'style':'width:10em'},
                             {'id':'cuenta','ui':'Cuenta', 'required':'true', 'style':'width:10em'},
                             {'id':'subcuenta','ui':'Subcuenta', 'required':'true', 'style':'width:10em'},
                      ],
            'Fruta':[
                     {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                     ],
            'LoteDeCompra':[
                            {'id':'fecha','ui':'Fecha', 'required':'true', 'style':'width:10em'},
                            {'id':'fruta','ui':'Fruta', 'required':'true', 'style':'width:10em'},
                            {'id':'proveedor','ui':'Proveedor', 'required':'true', 'style':'width:10em'},
                            {'id':'precio','ui':'Precio($/kg)', 'required':'true', 'style':'width:10em'},
                            {'id':'peso','ui':'Peso(kg)', 'required':'true', 'style':'width:10em'},
                            {'id':'procesado','ui':'Procesado', 'required':'true', 'style':'width:10em'},
                            ],
            'Clase':[
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                      ],
            'Grupo':[
                      {'id':'clase','ui':'Clase', 'required':'true', 'style':'width:10em'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                                            
                      ],
            'Cuenta':[
                      {'id':'grupo','ui':'Grupo', 'required':'true', 'style':'width:10em'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                      ],
            'SubCuenta':[
                      {'id':'cuenta','ui':'Cuenta', 'required':'true', 'style':'width:10em'},   
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'pucNumber','ui':'PUC No.', 'required':'true', 'style':'width:10em'},
                      ],
            'PorcionCompra':[
                             {'id':'valor','ui':'Porcion', 'required':'true', 'style':'width:10em'},
                             {'id':'unidades','ui':'Unidades', 'required':'true', 'style':'width:10em'}
                       ],
            'TipoEgreso':[
                          {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                          ],
            'Egreso':[
                      {'id':'numero','ui':'Numero','required':'true', 'style':'width:4em'},
                      {'id':'fecha', 'ui':'Fecha','style':'width:5em'},
                      {'id':'proveedor','ui':'Proveedor','style':'width:10em'},
                      {'id':'sucursal', 'ui':'Ciudad','style':'width:5em'},
                      {'id':'fuente', 'ui':'Fuente','style':'width:5em'},
                      #{'id':'tipo','ui':'Tipo','style':'width:5em'},
                      {'id':'resumen','ui':'Bien o Servicio','required':'true','style':'width:10em'},
                      {'id':'total','ui':'Valor','required':'true', 'style':'width:5em'},
                      #{'id':'empleado','ui':'Empleado','style':'width:10em'}
                      ],
            'TipoAcreedor':[
                          {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                          ],
            'Acreedor':[
                        {'id':'tipo','ui':'Tipo','style':'width:10em'},
                        {'id':'nombre','ui':'Nombre', 'required':'true',  'style':'width:10em'},
                        {'id':'nit','ui':'NIT', 'required':'true', 'style':'width:6em'},
                        {'id':'ciudad','ui':'Ciudad', 'required':'true', 'style':'width:5em'},
                        {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:8em'},
                        {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:5em'}
                        ],
            'Deuda':[
                     {'id':'numero','ui':'No.','readonly':'true','style':'width:2em','auto':''},
                     {'id':'fecha', 'ui':'Fecha','style':'width:7em'},
                     {'id':'empleado','ui':'Empleado','style':'width:8em'},
                     {'id':'acreedor','ui':'Acreedor','style':'width:8em'},
                     {'id':'monto','ui':'Monto','required':'true', 'style':'width:5em'},
                     {'id':'interes','ui':'Interes(EA)','required':'true', 'style':'width:5em','default':'0'},
                     {'id':'vencimiento', 'ui':'Vencimiento','style':'width:7em'},
                     {'id':'montoPagado', 'ui':'Monto Pagado','required':'true','style':'width: 5em','default':'0'},
                     {'id':'comentario', 'ui':'Comentario','required':'true','style':'width:10em;'},
#                      {'id':'pagada', 'ui':'% Pagado','required':'true','style':'width:3em','default':'0'},
                     ],
            'OtrosIngresos':[
                             {'id':'numero','ui':'No.','required':'true', 'readonly':'true','auto':'','style':'width:2em'},
                             {'id':'empleado','ui':'Empleado','style':'width:8em'},
                             {'id':'fecha', 'ui':'Fecha','style':'width:5em','required':'true'},
                             {'id':'descripcion', 'ui':'Descripcion','required':'true','style':'width:10em'},
                             {'id':'total','ui':'Monto','required':'true','style':'width:10em'}
                             ],
            'CapitalSocial':[
                             {'id':'socio','ui':'Socio', 'required':'true',  'style':'width:10em'},
                             {'id':'acciones','ui':'No. Acciones','required':'true','style':'width:10em'},
                             {'id':'total','ui':'Valor','required':'true','style':'width:10em'},
                             {'id':'participacion', 'ui':'Participacion (%)','required':'true','style':'width:8em', 'disabled':'true'}
                             ],
            'CapitalPagado':[
                             {'id':'fecha', 'ui':'Fecha','style':'width:10em','required':'true'},
                             {'id':'valor','ui':'Valor','required':'true','style':'width:10em'},
                             ],
            'ActivoFijo':[
                      {'id':'numero','ui':'No.','required':'true', 'style':'width:2em', 'readonly':'true', 'auto':'true'},
                      {'id':'fechaDeAdquisicion', 'ui':'Fecha de compra','style':'width:10em','required':'true'},
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                      {'id':'grupo','ui':'Grupo', 'required':'true', 'style':'width:8em'},
                      {'id':'cuenta','ui':'Cuenta', 'required':'true', 'style':'width:8em'},
                      {'id':'subcuenta','ui':'Subcuenta', 'required':'true', 'style':'width:8em'},
                      {'id':'valorPagado','ui':'Valor Pagado','required':'true','style':'width:8em'},
                      {'id':'valorActual','ui':'Valor Actual','required':'true','style':'width:8em'},
                      ],
            'CuentaBancaria':[
                              {'id':'banco','ui':'Banco','style':'width:10em'},
                              {'id':'tipo','ui':'Tipo de Cuenta','style':'width:5em'},
                              {'id':'numero','ui':'No.','required':'true', 'style':'width:10em'},
                              {'id':'titular','ui':'Titular', 'required':'true', 'style':'width:10em'},
                              ],
            'Banco':[
                     {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                     {'id':'direccion','ui':'Direccion', 'required':'true', 'style':'width:10em'},
                     {'id':'telefono','ui':'Telefono', 'required':'true', 'style':'width:10em'},
                     {'id':'contacto','ui':'Contacto', 'required':'false', 'style':'width:10em'},
                     ],
            'TipoDeCuenta':[
                            {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                            ],
            'SaldoCuentaBancaria':[
                                   {'id':'cuenta','ui':'Cuenta','style':'width:10em'},
                                   {'id':'fecha', 'ui':'Fecha','style':'width:7em'},
                                   {'id':'saldo', 'ui':'Saldo','style':'width:5em','required':'true','valid':'dijit/form/NumberTextBox'},
                                   ],
            'MedioDePago':[
                           {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'},
                           ],
            'CuentaTransferencias':[
                           {'id':'numero','ui':'No.','required':'true', 'style':'width:10em'},
                           {'id':'cliente','ui':'Cliente','style':'width:15em'},
                           ],
            'PagoRecibido':[
                              {'id':'numero','ui':'No.','required':'true', 'style':'width:2em','readonly':'true','auto':''},
                              {'id':'fecha', 'ui':'Fecha','style':'width:5em','required':'true'},
                              {'id':'cliente','ui':'Cliente','style':'width:15em'},
                              {'id':'medio','ui':'Medio de pago','style':'width:8em'},
                              {'id':'oficina','ui':'Oficina','style':'width:5em'},
                              {'id':'documento','ui':'Documento','required':'false', 'style':'width:5em'},
                              {'id':'monto','ui':'Monto','required':'true', 'style':'width:5em'},
                              {'id':'facturas','ui':'Facturas','required':'true', 'style':'width:10em'},
                              ],
            'Inventario':[
                          {'id':'sucursal','ui':'Sucursal','style':'width:5em'},
                          {'id':'fecha', 'ui':'Fecha','style':'width:5em','required':'true'},
                          ],
            'Produccion':[
                          {'id':'fecha', 'ui':'Fecha','style':'width:8em'},
                          #{'id':'sucursal','ui':'Sucursal','style':'width:5em'},
                          {'id':'fruta','ui':'Fruta', 'style':'width:10em'},
                          {'id':'pesoFruta','ui':'Peso Fruta (kg)','required':'true', 'style':'width:5em'},                          
                          {'id':'productos','ui':'Productos','style':'width:10em'},
                          {'id':'rendimiento','ui':'Rendimiento (%)','required':'false', 'style':'width:5em'},
                          {'id':'costoBruto','ui':'Costo Bruto ($/kg)','required':'false', 'style':'width:5em'}
                          ],
            'ProductoPorcion':[
                               {'id':'porcion','ui':'Porcion','style':'width:5em'},
                               {'id':'cantidad','ui':'Cantidad','style':'width:5em', 'required':'true', 'default':0}
                            ],
            'Compra':[
                      {'id':'cantidad','ui':'Cantidad','style':'width:5em', 'required':'true', 'default':0},
                      {}
                      ],
            'Fuente':[
                      {'id':'nombre','ui':'Nombre', 'required':'true', 'style':'width:10em'}
                    ]
            }

            
templateStrings = {'Remision':'/crearFactura?entityClass=Remision',
                'Factura':'/crearFactura?entityClass=Factura', 
                   'Egreso':'/crearEgreso',
                   'Inventario':'/dojoxLoader?entityClass=Inventario&template=crearInventario.html',
                   'tablaDinamica':'/tablaDinamica.html',
                   'InformeDePagos':'/InformeDePagos.html',
                   'numeros':'/numeros.html',
                   'pYg':'/pYg.html',
                   'CuentasPorCobrar':'/cuentasPorCobrar.html',
                   'Existencias':'/existencias.html',
                   'ConsolidarFactura':'consolidarFactura.html',
                   'EgresoFruta':'crearEgresoFruta.html'
                   }

templateParams = {'EgresoFruta':{'detalle':Compra._properties['detalle'],
                                 'cantidad':Compra._properties['cantidad'],
                                 'precio':Compra._properties['precio']
                                 }
                  }
detailFields = {
               'Factura':'ventas',
               'Remision':'ventas',
               'Egreso':'compras',
               'Inventario':'registros',
               'Produccion':'productos'
               }
exentosDeIVA = {
                'Materia.Prima-Fruta',
                'Nomina.-.Operativa',
                'Nomina-Turnos',
                'Nomina.-.Administrativa',
                'Taxis.y.Pasajes.de.Bus',
                'Servicios.Publicos-Energia',
                'Servicios.Publicos-Gas',
                'Servicios.Publicos-Agua',
                'Transporte.del.Producto-Local',
                'Transporte.del.Producto-Intermunicipal',
                'Mantenimiento.y.arreglos.locativos',
                'Alimentacion.Empleado'
                }


