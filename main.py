import webapp2
from myapp.controller.controller import *
from myapp.initSaludable import initSaludable

initSaludable()
application = webapp2.WSGIApplication([
    #User Management                                  
    ('/login',LogIn),
    ('/logout',LogOut),
    # Single Page App
    ('/home', Home),# The rooot of the 1-page app
    ('/getWidget',GetWidget),#Gets the right widget for each content pane in the 1-page app. 
    ('/dojoxLoader',DojoxLoader),#uses dojox to load remote html in a content pane with scripts enabled
    # saludable GENERAL
    ('/addEntity',AddEntity),
    ('/saveEntity', SaveEntity),
    ('/showEntities',ShowEntities),
    ('/entityData', EntityData),
    ('/getColumns', GetColumns),
    ('/deleteEntity', DeleteEntity),
    ('/getPrice', GetPrice),
#     ('/getVentas', GetVentas),
    ('/getProducto', GetProducto),
    ('/getPorcion', GetPorcion),
#     ('/getClientes', GetClientes),
    ('/getEmpleados', GetEmpleados),
    ('/getDetails',GetDetails),
    #CuentasPorCobrar
    ('/getCuentasPorCobrar', GetCuentasPorCobrar),
    ('/getDetalleCuentasPorCobrar', GetDetalleCuentasPorCobrar),
    #Inventario
    ('/guardarInventario',GuardarInventario),
    ('/getExistencias', GetExistencias),
    ('/getContenidoUnidadDeAlmacenamiento',GetContenidoUnidadDeAlmacenamiento),
    #Ingresos
    ('/guardarFactura', GuardarFactura),
    ('/mostrarFactura', MostrarFactura),
    ('/anularFactura', AnularFactura),
    ('/consolidarFactura',ConsolidarFactura),
    ('/getRemisionesByName',GetRemisionesByName),
    ('/crearOrdenDeSalida',CrearOrdenDeSalida),
    ('/crearFacturaFromPedido',CrearFacturaFromPedido),
    # Egresos
#     ('/crearEgreso', CrearEgreso),
    ('/guardarEgreso', GuardarEgreso),
    ('/guardarLoteDeCompra', GuardarLoteDeCompra),
    ('/getLotes',GetLotes),
    ('/getBienesoServicios',GetBienesoServicios),
    ('/getProveedores',GetProveedores),
    ('/addBienoservicio',Addbienoservicio),
#     ('/getCompras',GetCompras),
    # Data Management
    ('/exportScript', ExportScript),
    ('/importScript', ImportScript),
    ('/setNumero', SetNumber),
    ('/getNext', GetNextNumber),
    ('/importCSV', ImportCSV),
    # Informes
    ('/informePagos',GetInformePagos) ,
    ('/getProductSales',GetProductSales) ,
    ('/getAllCompras',GetAllCompras) ,
    ('/getPyG',PyG) ,
    ('/getIVAPagado',GetIVAPagado) ,
    ('/getEstadoDeResultados',GetEstadoDeResultados),
    ('/getDetalleEstadoDeResultados',GetDetalleEstadoDeResultados),
    ('/getPUC',GetPUC),
    ('/initPUC',InitPUC),
    #MISC
    ('/fix',Fix)
], debug=True)