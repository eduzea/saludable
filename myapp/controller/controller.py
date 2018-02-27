import json
import csv
from datetime import datetime, date
from datetime import timedelta
import sys
sys.path.insert(0, 'libs/python-dateutil-1.5')
sys.path.insert(0, 'libs/easydict-1.6')

import webapp2
from google.appengine.api import users

from myapp.view.view import JINJA_ENVIRONMENT
from myapp.config import templateStrings, detailFields, exentosDeIVA
from myapp.utilities.utils import createTemplateString, getColumns, prepareRecords, JSONEncoder, rreplace, fieldsInfo
from myapp.model.models import *
from myapp.initSaludable import dataStoreInterface
from myapp.initSaludable import initSaludable
# from estadosFinancieros import estadoDeResultados, detalleEstadoDeResultados
from myapp.controller.puntoDeEquilibrio import estadoDeResultados, detalleEstadoDeResultados,\
    detalleBalance, balance
from myapp.controller.followup import crearMovimientoDeInventario
from myapp.controller.importCSV import importCSV
from myapp.controller.PyG import getPyGData

#RUN INITIALIZACION CODE
initSaludable()

#### Define Request Handling functions ####

class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is not None:
            checkEmpleado(self,user)
        else:
            self.redirect(users.create_login_url('/home'))


def checkEmpleado(self,user):
    empleado = Empleado.query(Empleado.email == user.email()).get()
    if True:
        template_values = {'user': user}
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_values))
    else:
        tag = '<h1>No hay un usuario registrado con ese login en Salud-Able!</h1><br>'
        tag += '<h2>Pide al administrador eduzea@gmail.com que cree tu usuario.</h2><br>'
        tag += '<a href="/logout">Log out</a>'
        self.response.write(tag)
          
class LogOut(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/home'))

class GetWidget(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        temp_name = self.request.get('template')
        template_values = {}
        if temp_name: #its not the default CRUD template, load specifics
            template_values['template'] = temp_name
        else:
            template_values['template'] = 'crud'#carga los viewsx genericos de creacion y listado.
        template_values['entityClass']=entityClass
        template = JINJA_ENVIRONMENT.get_template("dojoxWidgetLoader.html")
        self.response.write(template.render(template_values))


# We use the Dojox Loader to be able to inject HTML + Javascript into the one-page application.
# If we just loaded the JINJA-HTML into a regular Content Pane, it would not run the associated scripts.
# Using dojox content pane allows us to group HTML and javascript into functional views
# that can be loaded on demand. 

class DojoxLoader(webapp2.RequestHandler):
    def get(self): 
        entityClass = self.request.get('entityClass')
        template = self.request.get('template')
        template_values = {}
        if entityClass in templateConfig:
            template_values['props'] = templateConfig[entityClass]()
        template_values['entityClass'] = entityClass
        template = JINJA_ENVIRONMENT.get_template(template + '.html')
        self.response.write(template.render(template_values))

class ShowEntities(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        template_values = {'entityClass': entityClass}
        template = JINJA_ENVIRONMENT.get_template('showEntities.html')
        self.response.write(template.render(template_values))

class GetColumns(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        self.response.write(json.dumps(getColumns(entityClass)))

class GetRemisionesByName(webapp2.RequestHandler):
    def get(self):
        razonSocial = self.request.get('razonSocial')
        clientes = Cliente.query(Cliente.nombre == razonSocial).fetch()
        clientes = [cliente.key for cliente in clientes]
        remisiones = dataStoreInterface.buildQuery('Remision', {'cliente':clientes, 'sortBy':'-numero'}).fetch()
        records = prepareRecords('Remision', remisiones)
        self.response.write(json.dumps(records))    

class EntityData(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass');
        simpleDict = {key: value for key,value in self.request.params.iteritems()}
        entity_query = dataStoreInterface.buildQuery(entityClass, simpleDict)
        count = self.request.get('count');
        if count:
            response = dataStoreInterface.getEntitiesByPage(self.request.get('cursor'),entityClass, entity_query, int(count))
            response['records']=prepareRecords(entityClass, response['records'])
        else:
            response = dataStoreInterface.getEntities(entityClass, entity_query)
            response['records']=prepareRecords(entityClass, response['records'])    
#         self.response.write(json.dumps(response))
        self.response.out.write(JSONEncoder().encode(response))

class SaveEntity(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        entityClass = values.pop("entityClass")     
        for key,value in values.iteritems():
            values[rreplace(key, '_' + entityClass,'',1)] = values.pop(key)
        response = dataStoreInterface.create_entity(entityClass,values)
        self.response.out.write(JSONEncoder().encode(response))

class AddEntity(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        template_values = {'entityClass': entityClass, 'fields': fieldsInfo(entityClass), 'auto':dataStoreInterface.autoNum(entityClass)}
        template = JINJA_ENVIRONMENT.get_template('addEntityForm.html')
        self.response.write(template.render(template_values))

class DeleteEntity(webapp2.RequestHandler):        
    def post(self):
        key = self.request.POST.get('key')
        entityClass = self.request.POST.get('entityClass')
        dataStoreInterface.deleteEntity(entityClass, key)
        self.response.out.write("Se elimino exitosamente: " + entityClass + " " + key)        

class GetClientes(webapp2.RequestHandler):
    def post(self):
        clientes = Cliente.query().fetch()
        clientes = [{'value':cliente.key.id(), 'name': cliente.rotulo } for cliente in clientes]
        self.response.out.write(json.dumps(clientes))
        
class GetEmpleados(webapp2.RequestHandler):
    def post(self):
        empleados = Empleado.query().fetch()
        empleados = [{'value':empleado.key.id(), 'name': empleado.rotulo } for empleado in empleados]
        self.response.out.write(json.dumps(empleados))
    
class GetProducto(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST.mixed()
        cliente = Cliente.get_by_id(post_data['cliente'])
        grupo = cliente.grupoDePrecios
        precios = Precio.query(Precio.grupoDePrecios == grupo,  projection = [Precio.producto], distinct=True).fetch()
        productos = [precio.producto.id() for precio in precios]
        if not productos:
            productos.append('No hay precios definidos')
        self.response.out.write(json.dumps(productos))
        
class GetPorcion(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST.mixed()
        porciones = []
        if 'producto' in post_data:
            producto= Producto.get_by_id(post_data['producto'])
            precios = []
            if 'cliente' in post_data:
                cliente = Cliente.get_by_id(post_data['cliente'])
                grupo = cliente.grupoDePrecios
                precios = Precio.query(Precio.grupoDePrecios == grupo,
                                       Precio.producto == producto.key,
                                       projection = [Precio.porcion], distinct=True).fetch()
            else:
                precios = Precio.query(Precio.producto == producto.key,
                                       projection = [Precio.porcion], distinct=True).fetch()
            porciones = [precio.porcion.id() for precio in precios]
        else:
            porciones = [porcion.key.id() for porcion in Porcion.query().fetch()]  
        self.response.out.write(json.dumps(porciones))        

class GetPrice(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        precioQuery = Precio.query(Precio.producto == Producto.get_by_id(values['producto']).key,
                                   Precio.grupoDePrecios == Cliente.get_by_id(values["cliente"]).grupoDePrecios,
                                   Precio.porcion == Porcion.get_by_id(values["porcion"]).key)
        precio = ''
        sujetoIVA = Producto.get_by_id(values['producto']).sujetoIVA
        try:
            precio = precioQuery.fetch()[0].precio
        except IndexError as e:
            self.response.out.write(e.message)
        self.response.out.write(json.dumps({'precio':precio,'sujetoIVA':sujetoIVA}))

# class GetBienesoServicios(webapp2.RequestHandler):
#     def get(self):
#         tipo = TipoEgreso.get_by_id(self.request.get('tipo'))
#         bienesoservicios = Bienoservicio.query(Bienoservicio.tipo == tipo.key, Bienoservicio.activo == True ).fetch()
#         response = [{'value':bienoservicio.key.id(), 'name': bienoservicio.rotulo } for bienoservicio in bienesoservicios]
#         self.response.out.write(json.dumps(response))

class GetBienesoServicios(webapp2.RequestHandler):
    def get(self):
        proveedor = Proveedor.get_by_id(self.request.get('proveedor'))
        bienesoservicios = proveedor.bienesoservicios
        response = [{'value':bienoservicio.id(), 'name': bienoservicio.id() } for bienoservicio in bienesoservicios]
        self.response.out.write(json.dumps(response))

        
class GetProveedores(webapp2.RequestHandler):
    def get(self):
        bienoservicio = Bienoservicio.get_by_id(self.request.get('bienoservicio'))
        todos = Proveedor.query()
        proveedores = todos.filter(Proveedor.bienesoservicios.IN([bienoservicio.key]), Proveedor.activo == True).fetch()
        response = [{'value':proveedor.key.id(), 'name': proveedor.rotulo } for proveedor in proveedores]
        self.response.out.write(json.dumps(response))


class GetMateriasPrimas(webapp2.RequestHandler):
    def get(self):
        tipo = self.request.get('tipo')
        mps = dataStoreInterface.buildQuery('MateriaPrima', {'bienoservicio':tipo})
        response = []
        for mp in mps:
            response.append({'label':mp.nombre,'value':mp.nombre})
        self.response.out.write(json.dumps(response))



class GetMateriasPrimasPorProducto(webapp2.RequestHandler):
    def get(self):
        producto = self.request.get('producto')
        mps = ndb.Key('Producto',producto).get().componentes
        response = []
        if len(mps) ==  0:
            response.append({'label':'NO HAY','value':''})
        else:
            for mp in mps:
                response.append({'label':mp.id(),'value':mp.id()})
        self.response.out.write(json.dumps(response))

class GetDetails(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        key = self.request.get('key')
        detailField = detailFields[entityClass]
        keyParts = keyDefs[entityClass]
        keyVals = key.split('.')
        filters = {}
        for keyPart,keyVal in zip(keyParts,keyVals):
            filters[keyPart]=keyVal
        qry = dataStoreInterface.buildQuery(entityClass,filters)
        parentRecord = qry.fetch()[0]
        response = {}
        for field in detailField:
            details = parentRecord.to_dict()[field]
            records=[]
            for detail in details:
                if type(detail) == ndb.Key:
                    detail = detail.get().to_dict()
                for prop_key, prop_value in detail.iteritems():
                    if type(prop_value) == ndb.Key:
                        try:
                            detail[prop_key] = detail[prop_key].id()#dicc[prop_key].get().to_dict()['rotulo']
                        except Exception as e:
                            detail[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
                    if type(prop_value) == date:
                        detail[prop_key] = prop_value.strftime('%Y-%m-%d')
    #             detail['id'] = getKey(detailField.capitalize(), detail)
                records.append(detail)
            response[field]=records
        self.response.out.write(json.dumps(response))


# class GetDetails(webapp2.RequestHandler):
#     def get(self):
#         entityClass = self.request.get('entityClass')
#         key = self.request.get('key')
#         detailField = detailFields[entityClass]
#         keyParts = keyDefs[entityClass]
#         keyVals = key.split('.')
#         filters = {}
#         for keyPart,keyVal in zip(keyParts,keyVals):
#             filters[keyPart]=keyVal
#         qry = dataStoreInterface.buildQuery(entityClass,filters)
#         parentRecord = qry.fetch()[0]
#         details = parentRecord.to_dict()[detailField]
#         records=[]
#         for detail in details:
#             if type(detail) == ndb.Key:
#                 detail = detail.get().to_dict()
#             for prop_key, prop_value in detail.iteritems():
#                 if type(prop_value) == ndb.Key:
#                     try:
#                         detail[prop_key] = detail[prop_key].id()#dicc[prop_key].get().to_dict()['rotulo']
#                     except Exception as e:
#                         detail[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
#                 if type(prop_value) == date:
#                     detail[prop_key] = prop_value.strftime('%Y-%m-%d')
# #             detail['id'] = getKey(detailField.capitalize(), detail)
#             records.append(detail)
#         self.response.out.write(json.dumps(records))
        
class GetEstadoDeResultados(webapp2.RequestHandler):
    def get(self):
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        data = estadoDeResultados(fechaDesde, fechaHasta)
        self.response.out.write(json.dumps({'records':data}))

class GetDetalleEstadoDeResultados(webapp2.RequestHandler):
    def get(self):
        clase = self.request.get('cuenta')
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        data = detalleEstadoDeResultados(clase, fechaDesde, fechaHasta)
        self.response.out.write(JSONEncoder().encode(data))

class GetBalance(webapp2.RequestHandler):
    def get(self):
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        data = balance(fechaDesde, fechaHasta)
        self.response.out.write(json.dumps({'records':data}))

class GetDetalleBalance(webapp2.RequestHandler):
    def get(self):
        clase = self.request.get('cuenta')
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        data = detalleBalance(clase, fechaDesde, fechaHasta)
        self.response.out.write(JSONEncoder().encode(data))



        
class GetAllVentas(webapp2.RequestHandler):
    def get(self):
        records = []
        ventas = dataStoreInterface.buildQuery('Venta', self.request.params).fetch()
        for venta in ventas:
            vDict = venta.to_dict()
            vDict['mesnum']=venta.fecha.month
            vDict['mes']=venta.fecha.strftime('%B')
            vDict['year']=venta.fecha.year
            records.append(vDict)
        response = {'records':records}
        self.response.out.write(JSONEncoder().encode(response))           

# class GetAllVentas(webapp2.RequestHandler):
#     def get(self):
#         records = []
#         entity_query = dataStoreInterface.buildQuery('Factura', self.request.params)
#         facturas = entity_query.fetch()
#         for factura in facturas:
#             if factura.anulada: continue
#             for venta in factura.ventas:
#                 try:
#                     venta = venta.to_dict()
#                     venta['peso']=venta['porcion'].get().valor * venta['cantidad']
#                     venta['ciudad']=factura.cliente.get().ciudad.get().rotulo
#                     venta['factura']=factura.numero
#                     venta['iva']=factura.iva
#                     venta['cliente']=factura.cliente.id()
#                     venta['fecha']=factura.fecha
#                     venta['fechaVencimiento']=factura.fechaVencimiento
#                     venta['mesnum']=factura.fecha.month
#                     venta['mes']=factura.fecha.strftime('%B')
#                     venta['year']=factura.fecha.year
#                 except Exception as e:
#                     print factura.numero, " : ", e.message
#                 records.append(venta)
#         response = {'records':records}
#         self.response.out.write(JSONEncoder().encode(response))           


class GetAllCompras(webapp2.RequestHandler):
    def get(self):
        records = []
        entity_query = dataStoreInterface.buildQuery('Compra', self.request.params)
        compras = entity_query.fetch()
        for compra in compras:
            compraDict = compra.to_dict()
            compraDict['mesnum']=compra.fecha.month
            compraDict['mes']=compra.fecha.strftime('%B')
            compraDict['year']=compra.fecha.year
            records.append(compraDict)
        response = {'records':records}
        self.response.out.write(JSONEncoder().encode(response))

#Read CSV File
def read_csv(file, json_file, format):
    
    return 

def csv2json(csvReader):
    csv_rows = []
    title = csvReader.fieldnames
    for row in csvReader:
        csv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])
    

#Convert csv data into json and write it
def write_json(data, json_file, format):
    with open(json_file, "w") as f:
        if format == "pretty":
            f.write(json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
        else:
            f.write(json.dumps(data))

class InitPUC(webapp2.RequestHandler):
    def get(self):
        records = []
        with open('data/PUC.csv') as csvfile:
            csvReader = csv.DictReader(csvfile)
            title = csvReader.fieldnames
            for row in csvReader:
                records.append({title[i].lower():row[title[i]] for i in range(len(title))})
        for record in records:
            if len(record['pucnumber']) == 1:
                dataStoreInterface.create_entity("Clase", record)
            if len(record['pucnumber']) == 2:
                dataStoreInterface.create_entity("Grupo", record)
            if len(record['pucnumber']) == 4:
                dataStoreInterface.create_entity("Cuenta", record)
            if len(record['pucnumber']) == 6:
                dataStoreInterface.create_entity("SubCuenta", record)
        self.response.out.write("Done with PUC init!")

#Function to provde the client with the PUC in json format
class GetPUC(webapp2.RequestHandler):
    def get(self):
        jsonRecords = []
        with open('data/PUC.csv') as csvfile:
            csvReader = csv.DictReader(csvfile)
            title = csvReader.fieldnames
            for row in csvReader:
                jsonRecords.append({title[i]:row[title[i]] for i in range(len(title))})
        self.response.out.write(json.dumps(jsonRecords))


# class CrearEgreso(webapp2.RequestHandler):
#     def get(self):
#         prop_tipo = Egreso._properties['tipo']
#         prop_proveedor = Egreso._properties['proveedor']
# #         prop_empleado = Egreso._properties['empleado']
#         prop_bienoservicio = Compra._properties['bienoservicio']
#         prop_detalle = Compra._properties['detalle']
#         prop_comentario = Egreso._properties['comentario']
#         prop_cantidad = Compra._properties['cantidad']
#         prop_precio = Compra._properties['precio']
#         prop_sucursal = Egreso._properties['sucursal']
#         prop_fuente = Egreso._properties['fuente']
#         empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
#         empleadoName = empleado.rotulo
#         empleadoValue = empleado.key.id()
#         props = {'proveedor':{'ui': 'Proveedor', 'id': 'proveedor','required':'true','type':prop_proveedor},
# #                  'empleado':{'ui': 'Empleado', 'id': 'empleado','required':'true','type':prop_empleado},
#                  'empleado': {'value':empleadoValue,'label':empleadoName},
#                  'bienoservicio':{'ui': 'Bien o Servicio', 'id': 'bienoservicio','required':'true','type':prop_bienoservicio},
#                  'detalle':{'ui': 'Detalle', 'id': 'detalle','required':'true','style':'width:10em','type':prop_detalle},
#                  'comentario':{'ui': 'Comentario', 'id': 'comentario','required':'false','style':'width:50em','type':prop_comentario},
#                  'cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true','style':'width:5em', 'type':prop_cantidad},
#                  'precio':{'ui':'Precio Unitario','id':'precio','required':'true','style':'width:5em', 'type':prop_precio},
#                  'tipo':{'ui':'Tipo', 'id':'tipo','required':'true','type':prop_tipo},
#                  'sucursal':{'ui':'Ciudad', 'id':'sucursal','required':'true','type':prop_sucursal},
#                  'fuente':{'ui':'Fuente', 'id':'fuente','required':'true','type':prop_fuente},
#                 }
#         template_values = {'props': props, 'entityClass':'Egreso'}
#         print template_values
#         template = JINJA_ENVIRONMENT.get_template('crearEgreso.html')
#         self.response.write(template.render(template_values))
def configEgreso():
    return {'proveedor':{'ui': 'Proveedor', 'id': 'proveedor','required':'true','type':Egreso._properties['proveedor']},
             'bienoservicio':{'ui': 'Bien o Servicio', 'id': 'bienoservicio','required':'true','type':Compra._properties['bienoservicio']},
             'detalle':{'ui': 'Detalle', 'id': 'detalle','required':'true','style':'width:10em','type':Compra._properties['detalle']},
             'comentario':{'ui': 'Comentario', 'id': 'comentario','required':'false','style':'width:50em','type':Egreso._properties['comentario']},
             'cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true','style':'width:5em', 'type':Compra._properties['cantidad']},
             'precio':{'ui':'Precio Unitario','id':'precio','required':'true','style':'width:5em', 'type':Compra._properties['precio']},
             'tipo':{'ui':'Tipo', 'id':'tipo','required':'true','type':Egreso._properties['tipo']},
             'sucursal':{'ui':'Ciudad', 'id':'sucursal','required':'true','type':Egreso._properties['sucursal']},
             'fuente':{'ui':'Fuente', 'id':'fuente','required':'true','type':Egreso._properties['fuente']},
            }

def getVentasFromPedido(cliente, lotes):
    ventas =[]
    total = 0
    for lote in lotes:
        precioQuery = Precio.query(Precio.producto ==lote.producto,
                                   Precio.grupoDePrecios == cliente.get().grupoDePrecios,
                                   Precio.porcion == lote.porcion)
        precio = precioQuery.fetch()[0].precio
        lote.precio = precio
        lote.venta = precio * lote.cantidad
        ventas.append(lote);
        total += precio * lote.cantidad
    return {'ventas':ventas, 'total':total}

class CrearFacturaFromPedido(webapp2.RequestHandler):
    def get(self):
        response = {}
        pedidoKey = self.request.get('pedido')
        pedido = Pedido.get_by_id(pedidoKey);
        if pedido.factura: # ya se facturo!
            response = {'result':'Success', 'id': pedido.factura.id()}
        else:
            #process inventory
            ods = getOrdenesDeSalida(pedido.items)
            if ods['movimientos']:
                for mi in ods['movimientos']:
                    crearMovimientoDeInventario(*mi)
                values = getVentasFromPedido(pedido.cliente,pedido.items)
                values['subtotal'] = values['total']
                values['empleado'] = Empleado.query(Empleado.email == users.get_current_user().email()).fetch()[0]
                values['fecha'] = pedido.fechaDeEntrega
                values['numero'] = dataStoreInterface.getConsecutivo('Factura')
                values['cliente'] = pedido.cliente
                factura = dataStoreInterface.create_entity('Factura', values)['entity']
                pedido.factura = factura.key
                pedido.put()
                response = {'result':'Success','id': factura.key.id()}
            else:
                response = {'result':'Failure','msg': 'Todo falta en el inventario!'}
        self.response.out.write(json.dumps(response))
    ########### Remember to create the movimientos de inventario 

def getOrdenesDeSalida(items):
    ordenes = []
    faltan = []
    movimientosDeInventario = []
    for item in items:
        params = {'producto':item.producto, 'porcion':item.porcion, 'sortBy':'fecha'}
        fdls = dataStoreInterface.buildQuery('FraccionDeLoteUbicado', params).fetch()
        cant = 0
        for fdl in fdls:
            lote = '{0}-{1}-{2}'.format(fdl.fecha.strftime('%Y-%m-%d'),fdl.producto.id(),fdl.porcion.id())
            orden = {'ubicacion':fdl.ubicacion,
                     'lote': lote
                    }
            if fdl.cantidad < item.cantidad - cant:                    
                orden['cantidad'] =  fdl.cantidad
                ordenes.append(orden)
                cant += fdl.cantidad
                movimientosDeInventario.append([fdl,'SALIDA', fdl.cantidad])
            else:
                orden['cantidad'] =  item.cantidad - cant
                ordenes.append(orden)
                cant = item.cantidad
                movimientosDeInventario.append([fdl,'SALIDA', fdl.cantidad])
                break
        if cant < item.cantidad:
            faltan.append({'producto':item.producto.id(), 'porcion':item.porcion.id(), 'cantidad':str(item.cantidad - cant)})
    return {'ordenes':ordenes, 'faltan':faltan, 'movimientos':movimientosDeInventario}    

class CrearOrdenDeSalida(webapp2.RequestHandler):
    def get(self):
        pedidoKey = self.request.get('pedido')
        pedido = Pedido.get_by_id(pedidoKey);
        ordenDeSalida = getOrdenesDeSalida(pedido.items)
        template = JINJA_ENVIRONMENT.get_template('ordenDeSalida.html')
        self.response.write(template.render({'pedido':pedido.numero,
                                             'cliente':pedido.cliente,
                                             'fecha':pedido.fechaDeEntrega,
                                             'ordenes':ordenDeSalida['ordenes'],
                                             'faltantes':ordenDeSalida['faltan'],
                                             }))


# class CrearFactura(webapp2.RequestHandler):
#     def get(self):
#         entityClass = self.request.get('entityClass')
#         prop_cliente = Factura._properties['cliente']
# #         prop_empleado = Factura._properties['empleado']
#         prop_producto = Venta._properties['producto']
#         prop_porcion = Venta._properties['porcion']
#         prop_cantidad = Venta._properties['cantidad']
#         empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
#         empleadoName = empleado.rotulo
#         empleadoValue = empleado.key.id()
#         props = {'Cliente':{'ui': 'Cliente', 'id': 'cliente','required':'true','type':prop_cliente},
#                  'Empleado': {'value':empleadoValue,'label':empleadoName},
#                  'Producto':{'ui': 'Producto', 'id': 'producto','required':'true','type':prop_producto},
#                  'Porcion':{'ui': 'Porcion', 'id': 'porcion','required':'true','type':prop_porcion},
#                  'Cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true',
#                          'style':'width:5em', 'type':prop_cantidad}
#             }
#         template_values = {'props': props, 'entityClass':entityClass}
#         template = JINJA_ENVIRONMENT.get_template('crearFactura.html')
#         self.response.write(template.render(template_values))

def configFactura():
        return {'Cliente':{'ui': 'Cliente', 'id': 'cliente','required':'true','type':Factura._properties['cliente']},
                 'Producto':{'ui': 'Producto', 'id': 'producto','required':'true','type':Venta._properties['producto']},
                 'Porcion':{'ui': 'Porcion', 'id': 'porcion','required':'true','type':Venta._properties['porcion']},
                 'Cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true',
                 'style':'width:5em', 'type':Venta._properties['cantidad']}
            }

        
class SetNumber(webapp2.RequestHandler):
    def get(self):
        tipo = self.request.get('tipo')
        newNumero = self.request.get('numero')
        msg ='Se definio el numero de ' + tipo +' actual como: ' + newNumero
        if 'Numero' + tipo in singletons:
            model = singletons['Numero' + tipo]
            numero = model.query().get()
            if numero:
                numero.consecutivo = int(newNumero)
                numero.put()
            else:
                model(consecutivo=int(newNumero)).put()
        else:
            msg = 'Parametro "tipo" debe estar en "singletons"'
        self.response.write(msg)

class GetNextNumber(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        self.response.write(dataStoreInterface.getConsecutivo(entityClass))

class GuardarFactura(webapp2.RequestHandler):        
    def post(self):
        empleado = dataStoreInterface.buildQuery('Empleado', {'email':users.get_current_user().email()}).get()
        response={}
        if not empleado.writePermission:
            response = {'result':'FAIL','message':"No tiene permiso de modificar el sistema"}
        else:
            post_data = self.request.body
            values = json.loads(post_data)
            values['empleado'] = empleado
            values['fecha'] = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
            values['numero'] = int(values['numero']) if values['numero']  else dataStoreInterface.getConsecutivo('Factura')
            ventas =[]
            gravado = 0
            exento = 0
            for venta in values['ventas']:
                venta['factura'] = values['numero']
                venta['fecha'] = values['fecha'] 
                venta['cliente'] = values['cliente']
                producto = venta['producto'].replace(' ','.')
                if Producto.get_by_id(producto).sujetoIVA:
                    gravado += int(venta['venta'])
                else:
                    exento += int(venta['venta'])
                entity = dataStoreInterface.create_entity('Venta',venta)['entity']
                ventas.append(entity)
            values['ventas'] = ventas
            values['gravado'] = gravado
            values['exento']= exento
            response = dataStoreInterface.create_entity('Factura', values)
            response = {'result':response['result'],'id': response['key'],"message":response['message']}
        self.response.out.write(json.dumps(response))

# class GuardarFactura(webapp2.RequestHandler):        
#     def post(self):
#         empleado = classModels['Empleado'].query(classModels['Empleado'].email == users.get_current_user().email()).get()
#         response={}
#         if not empleado.writePermission:
#             response = {'result':'FAIL','message':"No tiene permiso de modificar el sistema"}
#         else:
#             post_data = self.request.body
#             values = json.loads(post_data)
#             entityClass = values['entityClass']
#             ventas =[]
#             gravado = 0
#             exento = 0
#             for venta in values['ventas']:
#                 producto = venta['producto'].replace(' ','.')
#                 if Producto.get_by_id(producto).sujetoIVA:
#                     gravado += int(venta['venta'])
#                 else:
#                     exento += int(venta['venta'])
#                 ventas.append(Venta(producto=Producto.get_by_id(producto).key,
#                                porcion=Porcion.get_by_id(venta['porcion']).key,
#                                cantidad = venta['cantidad'],
#                                precio = venta['precio'],
#                                venta = venta['venta']))
#             values['ventas'] = ventas
#             values['gravado'] = gravado
#             values['exento']= exento
#             values['empleado'] = Empleado.query(Empleado.email == users.get_current_user().email()).fetch()[0]
#             values['fecha'] = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
#             values['numero'] = int(values['numero']) if values['numero']  else dataStoreInterface.getConsecutivo(entityClass)
#             response = dataStoreInterface.create_entity(entityClass, values)
#             response = {'result':response['result'],'id': response['key'],"message":response['message']}
#         self.response.out.write(json.dumps(response))
          
class MostrarFactura(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('id')
        entityClass = self.request.get('entityClass')
        facturaPorPagina = self.request.get('pagina')
        entity = classModels[entityClass].get_by_id(key)
        cliente = entity.cliente.get()
        empleado = entity.empleado.get()
        data = {'numero' : entity.numero,
                'cliente': unicode(cliente.rotulo),
                'direccion': unicode(cliente.direccion),
                'ciudad': unicode(cliente.ciudad.id()),
                'nit':cliente.nit, 
                'fecha': entity.fecha.strftime('%Y-%m-%d'),
                'telefono':cliente.telefono,
                'empleado': empleado.rotulo,
                'numVentas':len(entity.ventas),
                'total': '{:,.0f}'.format(entity.total),
                'peso':(entity.peso/1000.0),
                'iva': '{:,.0f}'.format(entity.montoIva),
                'gravado': '{:,.0f}'.format(entity.gravado),
                'exento':'{:,.0f}'.format(entity.exento),
                'remision': True if entityClass == 'Remision' else False,
                'remisiones': ', '.join(str(remision) for remision in entity.remisiones) if hasattr(entity, 'remisiones') else ''
                }
        ventas = []
        for venta in entity.ventas:
            ventas.append({'producto': venta.producto.get().rotulo, 'porcion':venta.porcion.id(), 'cantidad':venta.cantidad, 
                           'precio': '{:,}'.format(venta.precio), 'valorTotal':'{:,}'.format(venta.venta)})
                
        if facturaPorPagina == 'true':
            template = JINJA_ENVIRONMENT.get_template('Factura1p.htm')
        else:
            template = JINJA_ENVIRONMENT.get_template('Factura.htm')
        self.response.write(template.render({'data':data, 'ventas':ventas}))

class AnularFactura(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('id')
        entity = Factura.get_by_id(key)
        entity.anulada = True
        entity.put()
        self.response.write({'msg':'Se anulo Factura :' + key})
        
class ConsolidarFactura(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.body
        values = json.loads(post_data)
        values = [int(value) for value in values]
        remisiones = dataStoreInterface.buildQuery('Remision',{'numero':values}).fetch()
        ventas = {}
        nextFactura = dataStoreInterface.autoNum('Factura')
        for remision in remisiones:
            for venta in remision.ventas:
                key = venta.producto.id() + '.' + venta.porcion.id()
                if key in ventas:
                    ventas[key].cantidad += venta.cantidad
                    ventas[key].venta += venta.venta
                else:
                    ventas[key] = venta
            remision.factura = nextFactura
            remision.put()
        ventas = [venta for venta in ventas.itervalues()]
        subtotal = sum([venta.venta for venta in ventas])
        iva = 0.16 if remisiones[0].cliente.get().iva else 0
        empleado = Empleado.query(Empleado.email == users.get_current_user().email()).fetch()[0]
        values = {'numero':nextFactura,
                  'cliente':remisiones[0].cliente,
                  'fecha':date.today(),
                  'ventas':ventas,
                  'total': subtotal * (1 + iva),
                  'subtotal':subtotal,
                  'montoIva':subtotal * iva,
                  'empleado': empleado.key,
                  'pagada':False,
                  'remisiones':[remision.numero for remision in remisiones]
                  }
        response = dataStoreInterface.create_entity('Factura', values)['entity']
        self.response.out.write(JSONEncoder().encode(response))                

class GetInformePagos(webapp2.RequestHandler):
    def get(self):
        cliente = self.request.get('cliente')
        clienteNegocios = Cliente.query(Cliente.nombre == cliente).fetch()
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        factura_query = dataStoreInterface.buildQuery('Factura', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta,'cliente':[cliente.key for cliente in clienteNegocios]})
        facturas = factura_query.fetch()
        pagos_query = dataStoreInterface.buildQuery('PagoRecibido', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta,'cliente':[cliente.key for cliente in clienteNegocios]})
        pagos = pagos_query.fetch() 
        response = {'facturas': prepareRecords('Factura', facturas), 'pagos':pagos}
        self.response.out.write(JSONEncoder().encode(response)) 


class ImportCSV(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        datafile = self.request.get('datafile')
        importCSV('data/' + datafile, entityClass)
        self.response.write('Registros Importados!')

class ImportCashflow(webapp2.RequestHandler):
    def get(self):
        cuenta = self.request.get('cuenta')
        datafile = self.request.get('datafile')
        importCSV('data/' + datafile)
        
        
class GuardarInventario(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.body
        values = json.loads(post_data)
        registros =[]
        fecha = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
        sucursal = ndb.Key('Sucursal',values['sucursal'])
        for registro in values['registros']:
            producto = Producto.get_by_id(registro['producto']).key
            porcion = Porcion.get_by_id(registro['porcion']).key
            registroObj = dataStoreInterface.create_entity('InventarioRegistro',{'fecha' : fecha,
                                                              'sucursal' : sucursal,
                                                              'producto' : producto,
                                                              'porcion' : porcion,
                                                              'existencias' : registro['existencias']})['entity']
                                             
            registroObj.put()
            registros.append(registroObj.key)
        inventario = dataStoreInterface.create_entity('Inventario', {'fecha' : fecha,
                                                  'sucursal' : sucursal,
                                                  'registros': registros})['entity']
        inventario.put()
        self.response.out.write(json.dumps({'result':'Success','inventarioId': inventario.key.id()})) 

class PyG(webapp2.RequestHandler):
    def get(self):
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        pYgData = getPyGData(fechaDesde,fechaHasta)
        template = JINJA_ENVIRONMENT.get_template('PyG.htm')
        self.response.write(template.render(pYgData))

class GetIVA_PAGADO(webapp2.RequestHandler):
    def get(self):
        filters = {key: value for key,value in self.request.params.iteritems()}
        filters['sujetoIVA']=True
        compras = dataStoreInterface.buildQuery('Compra', filters).fetch()
        records = []
        compraDict = {}
        for compra in compras:
            compraDict = compra.to_dict()
            compraDict['iva']= int(compra.total * 0.19)
            records.append(compraDict)
        response = {'records':records, 'count':len(records)}
        return self.response.out.write(JSONEncoder().encode(response)) 

class GetIVA_RECAUDADO(webapp2.RequestHandler):
    def get(self):
        filters = {key: value for key,value in self.request.params.iteritems()}
        filters['sujetoIVA']=True
        ventas = dataStoreInterface.buildQuery('Venta', filters).fetch()
        records = []
        ventaDict = {}
        for venta in ventas:
            ventaDict = venta.to_dict()
            records.append(ventaDict)
        response = {'records':records, 'count':len(records)}
        return self.response.out.write(JSONEncoder().encode(response))

class ImportScript(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        json_data=open('data/' + entityClass +'.json')
        data = json.load(json_data)
#         data = json.loads(data)
        json_data.close()
        for record in data:
            print record
            dataStoreInterface.create_entity(entityClass, record)
        self.response.write('Registros Importados!')


class ExportScript(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        numRange = self.request.get('range')
        unpack = self.request.get('unpack').split(',')
        model = classModels[entityClass]
        data =[]
        if numRange:
            start = int(numRange.split('-')[0])
            end = int(numRange.split('-')[1])
            data = model.query(model.numero >= start, model.numero <= end).fetch()
        else:
            data = model.query().fetch()
        if unpack:
            encoder = JSONEncoder();
            encoder.unpack = unpack
            self.response.write(encoder.encode(data))
        else:
            self.response.write(JSONEncoder().encode(data))


class Addbienoservicio(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        property = self.request.get('property')
        id= self.request.get('id')
        classModels[entityClass]
        
class GuardarEgreso(webapp2.RequestHandler):        
    def post(self):
        empleado = classModels['Empleado'].query(classModels['Empleado'].email == users.get_current_user().email()).get()
        response={}
        if not empleado.writePermission:
            response = {'result':'FAIL','message':"No tiene permiso de modificar el sistema"}
        else:
            post_data = self.request.body
            values = json.loads(post_data)
            compras =[]
            values['numero'] = int(values['numero']) if values['numero'] else dataStoreInterface.getConsecutivo('Egreso')
            values['fecha'] = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
            for compra in values['compras']:
                compra['egreso'] = values['numero']
                compra['fecha'] = values['fecha']
                compra['proveedor'] = values['proveedor']
                compra['sucursal']=values['sucursal']
                compra['bienoservicio'] = compra['bienoservicio'].replace(' ','.').upper()
                entity = dataStoreInterface.create_entity('Compra',compra)['entity']
                compras.append(entity)
            values['empleado'] = Empleado.query(Empleado.email == users.get_current_user().email()).fetch()[0]
            values['resumen'] = compras[0].bienoservicio.id() #if len(compras)==1 else compras[0].bienoservicio.id() + ', etc.' #think of a better way to do this! 
            response = dataStoreInterface.create_entity('Egreso', values)
            response = {'result':response['result'],'id':response['key'],'message': response['message'] }
        self.response.out.write(json.dumps(response))

class GuardarLoteDeCompra(webapp2.RequestHandler):
    def get(self):
        egresoId = self.request.get('egresoId')
        egreso = Egreso.get_by_id(egresoId)
        for fruta in egreso.compras:
            values = {'fruta':ndb.Key(Fruta,fruta.detalle),
                      'proveedor': egreso.proveedor,
                      'fecha':egreso.fecha,
                      'precio':fruta.precio,
                      'peso':fruta.cantidad
                      }
            dataStoreInterface.create_entity('LoteDeCompra', values)
        self.response.out.write('Success')

class GetLotes(webapp2.RequestHandler):
    def get(self):
        materiaPrima = self.request.get('materiaPrima').replace('.',' ')
        lotes = dataStoreInterface.buildQuery('Compra',{'detalle':materiaPrima, 'procesado':False}).fetch()
        self.response.write(JSONEncoder().encode(lotes))

# Si se borra un cliente que sea referenciado en una factura esta function fallara
# No deberia ser posible borrar un cliente mientras haya facturas que lo referencien...
class GetCuentasPorCobrar(webapp2.RequestHandler):
    def get(self):
        response = []
        saldos={}
        facturas = Factura.query(Factura.pagada == False).fetch()
        for factura in facturas:
            cliente = factura.cliente.get()
            if not cliente: continue
            if cliente.nombre in saldos:
                saldos[cliente.nombre] += factura.total
            else:
                if cliente.activo == True and cliente.diasPago > 0  :
                    saldos[factura.cliente.get().nombre] =  factura.total
        for key,value in saldos.iteritems():
            response.append({'id':key,'cliente':key, 'monto':value})
        self.response.out.write(json.dumps(response))

class GetDetalleCuentasPorCobrar(webapp2.RequestHandler):
    def get(self):
        cliente = self.request.get('cliente')
        clienteNegocios = Cliente.query(Cliente.nombre == cliente).fetch()
        qry = dataStoreInterface.buildQuery('Factura', {'pagada':False, 'cliente':[cliente.key for cliente in clienteNegocios]})  
        facturas = qry.fetch()
        response = [{'id':factura.numero, 'factura':factura.numero,'fecha':factura.fecha,'negocio':factura.cliente.get().negocio,
                     'total':factura.total,'vencimiento':factura.fecha + timedelta(factura.cliente.get().diasPago),'vencida':diasVencida(factura)} for factura in facturas if not factura.pagada]
        self.response.out.write(JSONEncoder().encode(response))    

def diasVencida(factura):
    dias = factura.cliente.get().diasPago
    if datetime.today().date() > factura.fecha + timedelta(days=dias):
        return (datetime.today().date() - (factura.fecha + timedelta(days=dias))).days
    else:
        return 0

#Counts over UnidadesDeAlmacenamiento
class GetExistencias(webapp2.RequestHandler):
    def get(self):
        canastillas = UnidadDeAlmacenamiento.query().fetch()
        records = []
        for canastilla in canastillas:
            for fracc in canastilla.contenido:
                values = fracc.to_dict()
                values['ubicacion'] = canastilla.ubicacion
                records.append(values)
        self.response.write(JSONEncoder().encode(records)) 

#Directly uses de FraccionDeLote table.
class GetExistencias2(webapp2.RequestHandler):
    def get(self):
        records = FraccionDeLoteUbicado.query().fetch()
        self.response.write(JSONEncoder().encode(records)) 


class GetContenidoUnidadDeAlmacenamiento(webapp2.RequestHandler):
    def get(self):
        ubicacion = self.request.get('ubicacion')
        canastilla = UnidadDeAlmacenamiento.get_by_id(ubicacion)
        self.response.write(JSONEncoder().encode(canastilla.contenido))

def configEgresoFruta():
    return { 'proveedor' : {'type':Egreso._properties['proveedor']},
             'sucursal' : {'type':Egreso._properties['sucursal']},
             'fuente' : {'type':Egreso._properties['fuente']},
             'comentario' : {'type':Egreso._properties['comentario']},
             'detalle':{'type':Compra._properties['detalle']},
             'cantidad':{'type':Compra._properties['cantidad']},
             'precio':{'type':Compra._properties['precio']}
             }

def configNumero():
    return{ 'numero': {'type':Egreso._properties['numero'], 'id':'numerox','auto':''}
        }


templateConfig = {'Factura':configFactura,
                  'Egreso':configEgreso,
                  'crearEgresoFruta':configEgresoFruta,
                  'Numero':configNumero}


class Fix(webapp2.RequestHandler):
    def get(self):
        precios = dataStoreInterface.buildQuery('Precio', {} ).fetch()
        for precio in precios:
            precio.precio = int(precio.precio * 1.09) 
            precio.put()
        self.response.out.write('Done!')        

