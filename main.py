import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    #User Management                                  
    ('/test', Test),
    ('/login',LogIn),
    ('/logout',LogOut),
    ('/validateUser', ValidateUser),
    # Single Page App
    ('/home', Home),
    ('/getWidget',GetWidget),
    # CRUD GENERAL
    ('/addEntity',AddEntity),
    ('/saveEntity', SaveEntity),
    ('/showEntities',ShowEntities),
    ('/entityData', EntityData),
    ('/getColumns', GetColumns),
    ('/deleteEntity', DeleteEntity),
    ('/getPrice', GetPrice),
    ('/getVentas', GetVentas),
    ('/getProducto', GetProducto),
    ('/getPorcion', GetPorcion),
    ('/getClientes', GetClientes),
    ('/getEmpleados', GetEmpleados),
    #Ingresos
    ('/crearFactura', CrearFactura),
    ('/guardarFactura', GuardarFactura),
    ('/mostrarFactura', MostrarFactura),
    ('/anularFactura', AnularFactura),
    ('/importFacturas',ImportFacturas),    
    # Egresos
    ('/crearEgreso', CrearEgreso),
    ('/guardarEgreso', GuardarEgreso),
    ('/getBienesoServicios',GetBienesoServicios),
    ('/getProveedores',GetProveedores),
    ('/addBienoservicio',Addbienoservicio),
    ('/getCompras',GetCompras),
    # Data Management
    ('/exportScript', ExportScript),
    ('/importScript', ImportScript),
    ('/setNumero', SetNumber),
    ('/importCSV', ImportCSV),
    # Analisis
    ('/pivot',Pivot),
    ('/tablaDinamica',TablaDinamica),
    ('/getProductSales',GetProductSales) ,
    ('/fixPrecios',FixPrecios)
], debug=True)