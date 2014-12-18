import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    ('/test', Test),
    ('/login',LogIn),
    ('/logout',LogOut),
    ('/home', Home),
    ('/addEntity',AddEntity),
    ('/saveEntity', SaveEntity),
    ('/showEntities',ShowEntities),
    ('/entityData', EntityData),
    ('/deleteEntity', DeleteEntity),
    ('/crearFactura', CrearFactura),
    ('/getPrice', GetPrice),
    ('/guardarFactura', GuardarFactura),
    ('/exportScript', ExportScript),
    ('/importScript', ImportScript),
    ('/mostrarFactura', MostrarFactura),
    ('/getVentas', GetVentas),
    ('/getProducto', GetProducto),
    ('/getPorcion', GetPorcion),
    ('/getClientes', GetClientes),
    ('/getEmpleados', GetEmpleados),
    ('/setNumero', SetNumber),
    ('/importCSV', ImportCSV),
    ('/importFacturas',ImportFacturas),
    ('/anularFactura', AnularFactura),
    ('/pivot',Pivot),
    ('/tablaDinamica',TablaDinamica),
    ('/getProductSales',GetProductSales),
    ('/getWidget',GetWidget)
], debug=True)