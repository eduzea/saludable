import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    ('/test', Test),
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
#     ('/importarClientes', ImportClientes),
#     ('/importarProductos', ImportProductos),
#     ('/importarPorciones', ImportPorciones),
    ('/mostrarFactura', MostrarFactura),
    ('/getVentas', GetVentas),
    ('/getProducto', GetProducto),
    ('/getPorcion', GetPorcion),
    ('/getClientes', GetClientes),
    ('/getEmpleados', GetEmpleados),
    ('/setNumeroFactura', SetNumeroFactura)
], debug=True)