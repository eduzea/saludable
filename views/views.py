# -*- coding: utf-8 -*-

from __future__ import division
import sys
import csv
sys.path.insert(0, 'libs/python-dateutil-1.5')
sys.path.insert(0, 'libs/easydict-1.6')
import webapp2
import jinja2
from datastorelogic import *
from followup import *
from config import *
from utils import *
from PyG import *
from presentation import *
from importCSV import *
from puntoDeEquilibrio import *
from datetime import datetime
from datetime import timedelta


if 'dataStoreInterface' not in globals():
    dataStoreInterface = DataStoreInterface()

class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            checkEmpleado(self,user)
        else:
            self.redirect(users.create_login_url('/login'))


def checkEmpleado(self,user):
    empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
    if True:#empleado:
        template_values = {'user': user}
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_values))
    else:
        tag = '<h1>No hay un usuario registrado con ese login en Salud-Able!</h1><br>'
        tag += '<h2>Pide al administrador eduzea@gmail.com que cree tu usuario.</h2><br>'
        tag += '<a href="/logout">Log out</a>'
        self.response.write(tag)

class LogIn(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        checkEmpleado(self,user)
           
class LogOut(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/home'))

class GetWidget(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        temp_name = self.request.get('template')
        template_values = {}
        if temp_name in templateStrings:
            template_name = 'dojoxWidgetLoader.html'# This is used to wrap any template in the dojox content pane so the scripts can run. 
            template_values['template'] = templateStrings[temp_name]
        else:
            template_name = 'widget.html'#carga los views genericos de creacion y listado.
            template_values['template'] = createTemplateString(entityClass)
        template_values['entity_class']=entityClass
        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.write(template.render(template_values))

# HTML Templates can only be served from Python, unless they are put in static (which makes no sens if they are dynamic).
# Thus any template to be shown in Dojox content pane has to be served through python. This is a generic template
# serving request handler.        
class DojoxLoader(webapp2.RequestHandler):
    def get(self): 
        entityClass = self.request.get('entityClass')
        template_values = {}
        if entityClass in getTemplateData:
            template_values = getTemplateData[entityClass](self.request)
        template_values['entityClass'] = entityClass
        template = self.request.get('template')
        template = JINJA_ENVIRONMENT.get_template(template)
        self.response.write(template.render(template_values))


class ShowEntities(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        template_values = {'entity_class': entity_class}
        template = JINJA_ENVIRONMENT.get_template('showEntities.html')
        self.response.write(template.render(template_values))

class GetColumns(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        self.response.write(json.dumps(getColumns(entity_class)))

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
        entity_class = self.request.get('entityClass');
        simpleDict = {key: value for key,value in self.request.params.iteritems()}
        entity_query = dataStoreInterface.buildQuery(entity_class, simpleDict)
        count = self.request.get('count');
        if count:
            response = dataStoreInterface.getEntitiesByPage(self.request.get('cursor'),entity_class, entity_query, int(count))
            response['records']=prepareRecords(entity_class, response['records'])
        else:
            response = dataStoreInterface.getEntities(entity_class, entity_query)
            response['records']=prepareRecords(entity_class, response['records'])    
        self.response.write(json.dumps(response))        

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
        entity_class = self.request.get('entityClass')
        template_values = {'entityClass': entity_class, 'fields': fieldsInfo(entity_class), 'auto':dataStoreInterface.autoNum(entity_class)}
        template = JINJA_ENVIRONMENT.get_template('addEntity.html')
        self.response.write(template.render(template_values))

class DeleteEntity(webapp2.RequestHandler):        
    def post(self):
        key = self.request.POST.get('key')
        entityClass = self.request.POST.get('entity_class')
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
        try:
            precio = precioQuery.fetch()[0].precio
        except IndexError as e:
            self.response.out.write(e.message)
        self.response.out.write(precio)

class GetBienesoServicios(webapp2.RequestHandler):
    def get(self):
        tipo = TipoEgreso.get_by_id(self.request.get('tipo'))
        bienesoservicios = Bienoservicio.query(Bienoservicio.tipo == tipo.key).fetch()
        response = [{'value':bienoservicio.key.id(), 'name': bienoservicio.rotulo } for bienoservicio in bienesoservicios]
        self.response.out.write(json.dumps(response))

        
class GetProveedores(webapp2.RequestHandler):
    def get(self):
        bienoservicio = Bienoservicio.get_by_id(self.request.get('bienoservicio'))
        todos = Proveedor.query()
        proveedores = todos.filter(Proveedor.bienesoservicios.IN([bienoservicio.key]), Proveedor.activo == True).fetch()
        response = [{'value':proveedor.key.id(), 'name': proveedor.rotulo } for proveedor in proveedores]
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
        details = parentRecord.to_dict()[detailField]
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
        self.response.out.write(json.dumps(records))
        
class GetUtilidades(webapp2.RequestHandler):
    def get(self):
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        if self.request.get('detallado'):
            utilidadData = getUtilidadDataFull(fechaDesde, fechaHasta)
        else:
            utilidadData = getUtilidadData(fechaDesde, fechaHasta)
        self.response.out.write(json.dumps({'records':utilidadData}))
        
class GetProductSales(webapp2.RequestHandler):
    def get(self):
        records = []
        entity_query = dataStoreInterface.buildQuery('Factura', self.request.params)
        facturas = entity_query.fetch()
        for factura in facturas:
            if factura.anulada: continue
            for venta in factura.ventas:
                try:
                    venta = venta.to_dict()
                    venta['peso']=venta['porcion'].get().valor * venta['cantidad']
                    venta['ciudad']=factura.cliente.get().ciudad.get().rotulo
                    venta['factura']=factura.numero
                    venta['cliente']=factura.cliente.id()
                    venta['fecha']=factura.fecha
                    venta['fechaVencimiento']=factura.fechaVencimiento
                    venta['mesnum']=factura.fecha.month
                    venta['mes']=factura.fecha.strftime('%B')
                    venta['year']=factura.fecha.year
                except Exception as e:
                    print factura.numero, " : ", e.message
                records.append(venta)
        response = {'records':records}
        self.response.out.write(JSONEncoder().encode(response))           

class GetAllCompras(webapp2.RequestHandler):
    def get(self):
        records = []
        entity_query = dataStoreInterface.buildQuery('Egreso', self.request.params)
        egresos = entity_query.fetch()
        for egreso in egresos:
            for compra in egreso.compras:
                compra = compra.to_dict()
                compra['egreso']=egreso.numero
                try:
                    compra['proveedor']=egreso.proveedor.get().rotulo
                except Exception as e:
                    print egreso.proveedor
                compra['fecha']=egreso.fecha
                compra['mesnum']=egreso.fecha.month
                compra['mes']=egreso.fecha.strftime('%B')
                compra['year']=egreso.fecha.year
                compra['tipo']=ndb.Key('TipoEgreso',egreso.tipo.id().upper()).get().rotulo
                compra['sucursal']=ndb.Key('Sucursal',egreso.sucursal.id().upper()).get().rotulo
                records.append(compra)
        response = {'records':records}
        self.response.out.write(JSONEncoder().encode(response))

class CrearEgreso(webapp2.RequestHandler):
    def get(self):
        prop_tipo = Egreso._properties['tipo']
        prop_proveedor = Egreso._properties['proveedor']
#         prop_empleado = Egreso._properties['empleado']
        prop_bienoservicio = Compra._properties['bienoservicio']
        prop_detalle = Compra._properties['detalle']
        prop_comentario = Egreso._properties['comentario']
        prop_cantidad = Compra._properties['cantidad']
        prop_precio = Compra._properties['precio']
        prop_sucursal = Egreso._properties['sucursal']
        prop_fuente = Egreso._properties['fuente']
        empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
        empleadoName = empleado.rotulo
        empleadoValue = empleado.key.id()
        props = {'proveedor':{'ui': 'Proveedor', 'id': 'proveedor','required':'true','type':prop_proveedor},
#                  'empleado':{'ui': 'Empleado', 'id': 'empleado','required':'true','type':prop_empleado},
                 'empleado': {'value':empleadoValue,'label':empleadoName},
                 'bienoservicio':{'ui': 'Bien o Servicio', 'id': 'bienoservicio','required':'true','type':prop_bienoservicio},
                 'detalle':{'ui': 'Detalle', 'id': 'detalle','required':'true','style':'width:10em','type':prop_detalle},
                 'comentario':{'ui': 'Comentario', 'id': 'comentario','required':'false','style':'width:50em','type':prop_comentario},
                 'cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true','style':'width:5em', 'type':prop_cantidad},
                 'precio':{'ui':'Precio Unitario','id':'precio','required':'true','style':'width:5em', 'type':prop_precio},
                 'tipo':{'ui':'Tipo', 'id':'tipo','required':'true','type':prop_tipo},
                 'sucursal':{'ui':'Ciudad', 'id':'sucursal','required':'true','type':prop_sucursal},
                 'fuente':{'ui':'Fuente', 'id':'fuente','required':'true','type':prop_fuente},
                }
        template_values = {'props': props, 'entityClass':'Egreso'}
        print template_values
        template = JINJA_ENVIRONMENT.get_template('crearEgreso.html')
        self.response.write(template.render(template_values))

class CrearFactura(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        prop_cliente = Factura._properties['cliente']
#         prop_empleado = Factura._properties['empleado']
        prop_producto = Venta._properties['producto']
        prop_porcion = Venta._properties['porcion']
        prop_cantidad = Venta._properties['cantidad']
        empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
        empleadoName = empleado.rotulo
        empleadoValue = empleado.key.id()
        props = {'Cliente':{'ui': 'Cliente', 'id': 'cliente','required':'true','type':prop_cliente},
                 'Empleado': {'value':empleadoValue,'label':empleadoName},
                 'Producto':{'ui': 'Producto', 'id': 'producto','required':'true','type':prop_producto},
                 'Porcion':{'ui': 'Porcion', 'id': 'porcion','required':'true','type':prop_porcion},
                 'Cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true',
                         'style':'width:5em', 'type':prop_cantidad}
            }
        template_values = {'props': props, 'entityClass':entityClass}
        template = JINJA_ENVIRONMENT.get_template('crearFactura.html')
        self.response.write(template.render(template_values))
        
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

class GuardarFactura(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.body
        values = json.loads(post_data)
        entityClass = values['entity_class']
        ventas =[]
        for venta in values['ventas']:
            producto = venta['producto'].replace(' ','.')
            ventas.append(Venta(producto=Producto.get_by_id(producto).key,
                           porcion=Porcion.get_by_id(venta['porcion']).key,
                           cantidad = venta['cantidad'],
                           precio = venta['precio'],
                           venta = venta['venta']))
        values['ventas'] = ventas
        values['empleado'] = Empleado.query(Empleado.email == users.get_current_user().email()).fetch()[0]
        values['fecha'] = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
        values['numero'] = int(values['numero']) if values['numero']  else getConsecutivo(values['entity_class'])
        factura = dataStoreInterface.create_entity(entityClass, values)['entity']          
        self.response.out.write(json.dumps({'result':'Success','id': factura.key.id()}))     



# class GuardarFactura(webapp2.RequestHandler):        
#     def post(self):
#         post_data = self.request.body
#         values = json.loads(post_data)
#         entityClass = values['entity_class']
#         ventas =[]
#         for venta in values['ventas']:
#             producto = venta['producto'].replace(' ','.')
#             ventas.append(Venta(producto=Producto.get_by_id(producto).key,
#                            porcion=Porcion.get_by_id(venta['porcion']).key,
#                            cantidad = venta['cantidad'],
#                            precio = venta['precio'],
#                            venta = venta['venta']))
#         cliente = Cliente.get_by_id(values['cliente'])
#         empleado = Empleado.query(Empleado.email == users.get_current_user().email()).fetch()[0]
#         fecha = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
#         numero = ''
#         if values['numero']:
#             numero = values['numero']
#         else:
#             numero = getConsecutivo(values['entity_class'])
#         entity = classModels[entityClass].query(classModels[entityClass].numero == int(numero)).fetch()
#         if entity:
#             entity = entity[0]    
#             if entityClass in preSaveAction:
#                 preSaveAction[entityClass](entity)
#             entity.populate(numero=int(numero), cliente = cliente.key, empleado = empleado.key,
#                                           fecha = fecha, ventas=ventas, total=int(values['total']),subtotal=values['subtotal'],
#                                           montoIva=values['iva'])
#         else:
#             entity = classModels[entityClass](id=str(numero), numero=int(numero), cliente = cliente.key, empleado = empleado.key,
#                                  fecha = fecha, ventas=ventas, total=int(values['total']),subtotal=values['subtotal'],
#                                  montoIva=values['iva'])
#         entity.put()
#         if entityClass in postSaveAction:
#                 postSaveAction[entityClass](entity)
#         self.response.out.write(json.dumps({'result':'Success','id': entity.key.id()}))     
                
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
                'iva': '{:,.0f}'.format(entity.montoIva),
                'subtotal': '{:,.0f}'.format(entity.subtotal if entity.montoIva != 0 else 0),
                'exento':'{:,.0f}'.format(entity.subtotal if entity.montoIva==0 else 0),
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
        tipo = self.request.get('tipo')
        if tipo == 'Factura':
            entity = Factura.get_by_id(key)
        else:
            entity = Remision.get_by_id(key)
        entity.anulada = True
        entity.put()
        self.response.write('Se anulo ' + tipo + ' :' + key)
        
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

class GetIVAPagado(webapp2.RequestHandler):
    def get(self):
        simpleDict = {key: value for key,value in self.request.params.iteritems()}
        entity_query = dataStoreInterface.buildQuery('Egreso', simpleDict)
        egresos = entity_query.fetch()
        records = []
        for egreso in egresos:
            egresoDicc = egreso.to_dict()
            if not egreso.resumen in exentosDeIVA:
                egresoDicc['subTotal'] = int(egreso.total/1.16)
                egresoDicc['ivaPagado'] = egreso.total - egresoDicc['subTotal']
                records.append(egresoDicc)
        response = {'records':records, 'count':len(records)}
        return self.response.out.write(JSONEncoder().encode(response)) 

class ImportScript(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        json_data=open('data/' + entity_class +'.json')
        data = json.load(json_data)
#         data = json.loads(data)
        json_data.close()
        for record in data:
            print record
            dataStoreInterface.create_entity(entity_class, record)
        self.response.write('Registros Importados!')


class ExportScript(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        numRange = self.request.get('range')
        unpack = self.request.get('unpack').split(',')
        model = classModels[entity_class]
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
        entity_class = self.request.get('entityClass')
        property = self.request.get('property')
        id= self.request.get('id')
        classModels[entity_class]
        
class GuardarEgreso(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.body
        values = json.loads(post_data)
        compras =[]
        for compra in values['compras']:
            bienoservicio = compra['bienoservicio'].replace(' ','.').upper()
            compras.append(Compra(bienoservicio=Bienoservicio.get_by_id(bienoservicio).key,
                           detalle = compra['detalle'],
                           cantidad = compra['cantidad'],
                           precio = compra['precio'],
                           compra = compra['compra']))
        values['empleado'] = Empleado.query(Empleado.email == users.get_current_user().email()).fetch()[0]
        values['fecha'] = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
        values['numero'] = int(values['numero']) if values['numero'] else getConsecutivo('Egreso')  
        values['resumen'] = compras[0].bienoservicio.id() #if len(compras)==1 else compras[0].bienoservicio.id() + ', etc.' #think of a better way to do this! 
        
        entity = dataStoreInterface.create_entity('Egreso', values)['entity']
        self.response.out.write(json.dumps({'result':'Success','egresoId': entity.key.id()}))

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
        fruta = self.request.get('fruta')
        lotes = dataStoreInterface.buildQuery('LoteDeCompra',{'fruta':fruta, 'procesado':False}).fetch()
        self.response.write(JSONEncoder().encode(lotes))

class GetCuentasPorCobrar(webapp2.RequestHandler):
    def get(self):
        response = []
        saldos={}
        facturas = Factura.query(Factura.pagada == False).fetch()
        for factura in facturas:
            if factura.cliente.get().nombre in saldos:
                saldos[factura.cliente.get().nombre] += factura.total
            else:
                if factura.cliente.get().activo == True:
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
class GetExistencias2(webapp2.RequestHandler):
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
class GetExistencias(webapp2.RequestHandler):
    def get(self):
        records = FraccionDeLoteUbicado.query().fetch()
        self.response.write(JSONEncoder().encode(records)) 


class GetContenidoUnidadDeAlmacenamiento(webapp2.RequestHandler):
    def get(self):
        ubicacion = self.request.get('ubicacion')
        canastilla = UnidadDeAlmacenamiento.get_by_id(ubicacion)
        self.response.write(JSONEncoder().encode(canastilla.contenido))

class Fix(webapp2.RequestHandler):
    def get(self): 
        params = {'cliente':['VENTOLINI.S.A'], 'pagada':False, 'fechaHasta':'2016-05-24'}
        facturas = dataStoreInterface.buildQuery('Factura',params).fetch()
        for factura in facturas:
            factura.pagada = True
            factura.put()
        self.response.out.write("System time: " + str(datetime.now()))





