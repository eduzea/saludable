# -*- coding: utf-8 -*-
from __future__ import division
import sys
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


class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
            if empleado:
                template_values = {'user': user}
                template = JINJA_ENVIRONMENT.get_template('home.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect(users.create_login_url('/login'))
        else:
            self.redirect(users.create_login_url('/login'))

class LogIn(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/validateUser'))

class ValidateUser(webapp2.RequestHandler):
    def get(self):
        empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
        if empleado:
            self.redirect(users.create_login_url('/home'))
        else:
            tag = '<h1>No hay un usuario registrado con ese login en Salud-Able!</h1><br>'
            tag += '<h2>Pide al administrador eduzea@gmail.com que cree tu usuario.</h2><br>'
            tag += '<a href="/logout">Log out</a>'
            self.response.write(tag)
            
class LogOut(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/login'))

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

class EntityData(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass');
        simpleDict = {key: value for key,value in self.request.params.iteritems()}
        entity_query = buildQuery(entity_class, simpleDict)
        count = self.request.get('count');
        if count:
            response = getEntitiesByPage(entity_class, entity_query, int(count), self)
            response['records']=prepareRecords(entity_class, response['records'])
        else:
            response = getEntities(entity_class, self, entity_query)
            response['records']=prepareRecords(entity_class, response['records'])    
        self.response.write(json.dumps(response))        

class SaveEntity(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        entityClass = values.pop("entityClass")     
        for key,value in values.iteritems():
            values[rreplace(key, '_' + entityClass,'',1)] = values.pop(key)
        response = create_entity(entityClass,values)
        if response['message'] == 'Updated':
            if entityClass in preSaveAction: 
                preSaveAction[entityClass](response['old'])
        if entityClass in postSaveAction:
            postSaveAction[entityClass](response['entity'])
        self.response.out.write(JSONEncoder().encode(response))

class AddEntity(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        template_values = {'entityClass': entity_class, 'fields': fieldsInfo(entity_class), 'auto':autoNum(entity_class)}
        template = JINJA_ENVIRONMENT.get_template('addEntity.html')
        self.response.write(template.render(template_values))

class DeleteEntity(webapp2.RequestHandler):        
    def post(self):
        key = self.request.POST.get('key')
        entity_class = self.request.POST.get('entity_class')
        try:
            entity = classModels[entity_class].get_by_id(key)
            entity.key.delete()
        except Exception as ex:
            self.response.out.write(ex.message)
            return
        if entity_class in postDeleteAction:
            postDeleteAction[entity_class](entity)
        self.response.out.write("Se elimino exitosamente: " + entity_class + " " + key)        

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
        proveedores = todos.filter(Proveedor.bienesoservicios.IN([bienoservicio.key])).fetch()
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
        qry = buildQuery(entityClass,filters)
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
        
        
class GetProductSales(webapp2.RequestHandler):
    def get(self):
        records = []
        entity_query = buildQuery('Factura', self.request.params)
        facturas = entity_query.fetch()
        for factura in facturas:
            if factura.anulada: continue
            for venta in factura.ventas:
                venta = venta.to_dict()
                venta['peso']=venta['porcion'].get().valor * venta['cantidad']
                venta['ciudad']=factura.cliente.get().ciudad.get().rotulo
                venta['factura']=factura.numero
                venta['cliente']=factura.cliente.id()
                venta['fecha']=factura.fecha
                venta['mesnum']=factura.fecha.month
                venta['mes']=factura.fecha.strftime('%B')
                venta['year']=factura.fecha.year
                records.append(venta)
        response = {'records':records}
        self.response.out.write(JSONEncoder().encode(response))           

class GetAllCompras(webapp2.RequestHandler):
    def get(self):
        records = []
        entity_query = buildQuery('Egreso', self.request.params)
        egresos = entity_query.fetch()
        for egreso in egresos:
            for compra in egreso.compras:
                compra = compra.to_dict()
                compra['egreso']=egreso.numero
                compra['proveedor']=egreso.proveedor.get().rotulo
                compra['fecha']=egreso.fecha
                compra['mesnum']=egreso.fecha.month
                compra['mes']=egreso.fecha.strftime('%B')
                compra['year']=egreso.fecha.year
                compra['tipo']=egreso.tipo.get().rotulo
                compra['sucursal']=egreso.sucursal.get().rotulo
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
                 'sucursal':{'ui':'Ciudad', 'id':'sucursal','required':'true','type':prop_sucursal}
                }
        template_values = {'props': props, 'entityClass':'Egreso'}
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
        cliente = Cliente.get_by_id(values['cliente'])
        empleado = Empleado.get_by_id(values['empleado'])
        fecha = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
        numero = ''
        if values['numero']:
            numero = values['numero']
        else:
            numero = getConsecutivo(values['entity_class'])
        entity = classModels[entityClass].query(classModels[entityClass].numero == int(numero)).fetch()
        if entity:
            entity = entity[0]    
            if entityClass in preSaveAction:
                preSaveAction[entityClass](entity)
            entity.populate(numero=int(numero), cliente = cliente.key, empleado = empleado.key,
                                          fecha = fecha, ventas=ventas, total=int(values['total']),subtotal=values['subtotal'],
                                          montoIva=values['iva'])
        else:
            entity = classModels[entityClass](id=str(numero), numero=int(numero), cliente = cliente.key, empleado = empleado.key,
                                 fecha = fecha, ventas=ventas, total=int(values['total']),subtotal=values['subtotal'],
                                 montoIva=values['iva'])
        entity.put()
        if entityClass in postSaveAction:
                postSaveAction[entityClass](entity)
        self.response.out.write(json.dumps({'result':'Success','id': entity.key.id()}))     
                
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
                'ciudad': unicode(cliente.ciudad.get().rotulo),
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
        remisiones = buildQuery('Remision',{'numero':values}).fetch()
        ventas = {}
        nextFactura = autoNum('Factura')
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
        response = create_entity('Factura', values)['entity']
        self.response.out.write(JSONEncoder().encode(response))                
        
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
            registroObj = create_entity('InventarioRegistro',{'fecha' : fecha,
                                                              'sucursal' : sucursal,
                                                              'producto' : producto,
                                                              'porcion' : porcion,
                                                              'existencias' : registro['existencias']})['entity']
                                             
            registroObj.put()
            registros.append(registroObj.key)
        inventario = create_entity('Inventario', {'fecha' : fecha,
                                                  'sucursal' : sucursal,
                                                  'registros': registros})['entity']
        inventario.put()
        if 'Inventario' in postSaveAction:
                postSaveAction['Inventario'](inventario)
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
        entity_query = buildQuery('Egreso', simpleDict)
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
            create_entity(entity_class, record)
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
            bienoservicio = compra['bienoservicio'].replace(' ','.')
            compras.append(Compra(bienoservicio=Bienoservicio.get_by_id(bienoservicio).key,
                           detalle = compra['detalle'],
                           cantidad = compra['cantidad'],
                           precio = compra['precio'],
                           compra = compra['compra']))
        proveedor = Proveedor.get_by_id(values['proveedor'])
        empleado = Empleado.get_by_id(values['empleado'])
        fecha = datetime.strptime(values['fecha'], '%Y-%m-%d').date()
        tipo = TipoEgreso.get_by_id(values['tipo'])
        sucursal = Sucursal.get_by_id(values['sucursal'])
        numero = ''
        if values['numero']:
            numero = values['numero']
        else:
            numero = getConsecutivoEgreso()

        resumen = compras[0].bienoservicio.id() #if len(compras)==1 else compras[0].bienoservicio.id() + ', etc.' #think of a better way to do this! 
        egreso = Egreso(id=str(numero), numero=int(numero), resumen = resumen, tipo = tipo.key, proveedor = proveedor.key, 
                        empleado = empleado.key, fecha = fecha, compras=compras, total=values['total'], sucursal = sucursal.key,
                        comentario = values['comentario'])
        egreso.put()
        entity = egreso
        self.response.out.write(json.dumps({'result':'Success','egresoId': entity.key.id()}))

class GetCuentasPorCobrar(webapp2.RequestHandler):
    def get(self):
        response = []
        saldos={}
        facturas = Factura.query(Factura.pagada == False).fetch()
        for factura in facturas:
            if factura.cliente.get().nombre in saldos:
                saldos[factura.cliente.get().nombre] += ( factura.total-sum(factura.abono) )
            else:
                saldos[factura.cliente.get().nombre] = ( factura.total- sum(factura.abono) )
        for key,value in saldos.iteritems():
            response.append({'id':key,'cliente':key, 'monto':value})
        self.response.out.write(json.dumps(response))

class GetDetalleCuentasPorCobrar(webapp2.RequestHandler):
    def get(self):
        cliente = self.request.get('cliente')
        clienteNegocios = Cliente.query(Cliente.nombre == cliente).fetch()
        qry = buildQuery('Factura', {'pagada':False, 'cliente':[cliente.key for cliente in clienteNegocios]})  
        facturas = qry.fetch()
        response = [{'id':factura.numero, 'factura':factura.numero,'fecha':factura.fecha,'negocio':factura.cliente.get().negocio,'total':factura.total, 'abono':sum(factura.abono)} for factura in facturas if not factura.pagada]
        self.response.out.write(JSONEncoder().encode(response))    
    
class GetExistencias(webapp2.RequestHandler):
    def get(self):
        existencias = Existencias.query().fetch()
        records = []
        if existencias:
            for existenciasCiudad in existencias:
                for registro in existenciasCiudad.registros:
                    entity = registro.get()
                    records.append({'id': entity.producto.id() + '.' + entity.porcion.id(), 
                                    'sucursal':entity.sucursal.id(),
                                    'producto':entity.producto.id(),
                                    'porcion':entity.porcion.id(),
                                    'existencias':entity.existencias})
        self.response.write(json.dumps(records)) 

class Fix(webapp2.RequestHandler):
    def get(self):
#         existencias = Existencias.query().fetch()
#         for existencia in existencias:
#             existencia.key.delete()
        inventarios = Inventario.query().fetch()
        for inventario in inventarios:
            for registro in inventario.registros:
                registro.delete()
            inventario.key.delete()
        self.response.out.write('Done!')
