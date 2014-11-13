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
    ('/mostrarFactura', MostrarFactura),
    ('/importarClientes', ImportClientes),
    ('/importarProductos', ImportProductos),
    ('/importarPorciones', ImportPorciones)
], debug=True)