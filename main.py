import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    #User Management                                  
    ('/login',LogIn),
    ('/logout',LogOut),
    ('/validateUser', ValidateUser),
    # Single Page App
    ('/home', Home),# The rooot of the 1-page app
    ('/getWidget',GetWidget),#Gets the right widget for each content pane in the 1-page app. 
    ('/dojoxLoader',DojoxLoader),#uses dojox to load remote html in a content pane with scripts enabled
    # CRUD GENERAL
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
    #Ingresos
    ('/crearFactura', CrearFactura),
    ('/guardarFactura', GuardarFactura),
    ('/mostrarFactura', MostrarFactura),
    ('/anularFactura', AnularFactura),
    ('/consolidarFactura',ConsolidarFactura),
    ('/getRemisionesByName',GetRemisionesByName),
    # Egresos
    ('/crearEgreso', CrearEgreso),
    ('/guardarEgreso', GuardarEgreso),
    ('/getBienesoServicios',GetBienesoServicios),
    ('/getProveedores',GetProveedores),
    ('/addBienoservicio',Addbienoservicio),
#     ('/getCompras',GetCompras),
    # Data Management
    ('/exportScript', ExportScript),
    ('/importScript', ImportScript),
    ('/setNumero', SetNumber),
    ('/importCSV', ImportCSV),
    # Informes
    ('/informePagos',GetInformePagos) ,
    ('/getProductSales',GetProductSales) ,
    ('/getAllCompras',GetAllCompras) ,
    ('/getPyG',PyG) ,
    ('/getIVAPagado',GetIVAPagado) ,
    #MISC
    ('/fix',Fix)
], debug=True)