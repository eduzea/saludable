'''
Created on Jul 25, 2015

@author: eduze_000
'''
from models.models import *
from datetime import datetime, date, time
from datastorelogic import DataStoreInterface


# Create the Instance - this approach is suspect...

if 'dataStoreInterface' not in globals():
    dataStoreInterface = DataStoreInterface()
####################### PAGO RECIBIDO Y CUENTAS POR COBRAR ###################################
def removePayment(pago):
    return
#     facturasAjustadas = Factura.query(Factura.pagoRef == pago.numero).fetch()
#     facturasAjustadas.sort(key=lambda factura: factura.numero)
#     for factura in facturasAjustadas:
#         factura.pagada = False
#         index = factura.pagoRef.index(pago.numero)
#         factura.pagoRef.remove(pago.numero)
#         if factura.abono:
#             del factura.abono[index]
#         factura.put()          

def updateFacturas(pago):
    for facturaId in pago.facturas:
        factura = Factura.get_by_id(str(facturaId))
        if factura:
            factura.pagada = True
            factura.pagoRef = pago.numero
            factura.put()
        else:
            raise Exception('Factura referenciada en el pago no existe! : ' + str(facturaId))        

dataStoreInterface.registerFollowUpLogic('pre', 'update', 'PagoRecibido', removePayment)
dataStoreInterface.registerFollowUpLogic('post', 'update', 'PagoRecibido', updateFacturas)
dataStoreInterface.registerFollowUpLogic('post', 'create', 'PagoRecibido', updateFacturas)
dataStoreInterface.registerFollowUpLogic('post', 'delete', 'PagoRecibido', removePayment)


######################### INVENTARIO Y EXISTENCIAS ################################
def updateFraccionDeLote(unidadDeAlmacenamiento):
    for fraccionDeLote in unidadDeAlmacenamiento.contenido:
        values = fraccionDeLote.to_dict()
        values['ubicacion'] =  unidadDeAlmacenamiento.key.id()
        flu = dataStoreInterface.create_entity('FraccionDeLoteUbicado',values)['entity'] 
        flu.put()

dataStoreInterface.registerFollowUpLogic('post', 'create', 'UnidadDeAlmacenamiento', updateFraccionDeLote)
dataStoreInterface.registerFollowUpLogic('post', 'update', 'UnidadDeAlmacenamiento', updateFraccionDeLote)

def removeFraccionDeLoteUbicado(fdl, ubicacion):
    values = fdl.to_dict()
    params = {'fecha':values['fecha'],'producto':values['producto'], 'porcion':values['porcion']}
    entities = dataStoreInterface.buildQuery('FraccionDeLoteUbicado',params).fetch()
    for entity in entities:
        entity.key.delete()
        

def updateUnidadDeAlamcenamiento(mi):
    ubicacion = mi.ubicacion
    canastilla = UnidadDeAlmacenamiento.query(UnidadDeAlmacenamiento.key == ubicacion).fetch()[0]
    presente = False
    for idx,fdl in enumerate(canastilla.contenido):
        if fdl.rotulo == mi.lote.id(): #lote is in canastilla
            presente = True
            tipo = -1 if mi.tipo.id() == 'SALIDA' else 1
            fdl.cantidad = fdl.cantidad + tipo * mi.cantidad
            if fdl.cantidad == 0:
                removeFraccionDeLoteUbicado(fdl, canastilla.ubicacion)
                canastilla.contenido.remove(fdl)
            else:
                canastilla.contenido[idx] = fdl
            canastilla.put()
                
    if not presente: # its a new lote
        values = {'fecha':mi.fecha, 'producto':mi.producto, 'porcion': mi.porcion, 'cantidad':mi.cantidad}
        fdl = FraccionDeLote(**values)
        canastilla.contenido.append(fdl)
        canastilla.put()
    
    updateFraccionDeLote(canastilla)

dataStoreInterface.registerFollowUpLogic('post', 'create', 'MovimientoDeInventario', updateUnidadDeAlamcenamiento)
dataStoreInterface.registerFollowUpLogic('post', 'update', 'MovimientoDeInventario', updateUnidadDeAlamcenamiento)

################# PEDIDOS ####################################

def validarPedido(pedido):
    items = pedido.items
    ordenDeSalida = []
    faltan=[]
    for item in items:
        params = {'producto':item.producto, 'porcion':item.porcion, 'sortBy':'fecha'}
        fdls = dataStoreInterface.buildQuery('FraccionDeLoteUbicado', params).fetch()
        cant = 0
        for fdl in fdls:
            orden = {'ubicacion':fdl.ubicacion,
                     'fecha':fdl.fecha.strftime('%Y-%m-%d'),
                     'producto':fdl.producto.id(),
                     'porcion':fdl.porcion.id()}
            cant += fdl.cantidad
            if cant < item.cantidad:
                orden['cantidad'] =  fdl.cantidad
                ordenDeSalida.append(orden)
                crearMovimientoDeInventario(fdl,'SALIDA', fdl.cantidad)
            else:
                orden['cantidad'] =  cant - item.cantidad
                ordenDeSalida.append(orden)
                crearMovimientoDeInventario(fdl,'SALIDA', cant - item.cantidad)
                break
        if cant < item.cantidad:
            faltan.append({'producto':item.producto.id(), 'porcion':item.porcion.id(), 'cantidad':str(item.cantidad - cant)})
    print ordenDeSalida, faltan #This should be used to create the printout of the orden de salida
                    
def crearMovimientoDeInventario(fdl, tipo, cantidad):
    params = {'fechaMovimiento' : datetime.today(),
              'ubicacion' : fdl.ubicacion,
              'tipo' : tipo,
              'fecha' : fdl.fecha,
              'producto' : fdl.producto,
              'porcion' : fdl.porcion,
              'cantidad' : cantidad}
    return dataStoreInterface.create_entity('MovimientoDeInventario', params)['entity']
            
####################!!!! incomplete


dataStoreInterface.registerFollowUpLogic('post', 'create', 'Pedido', validarPedido)
dataStoreInterface.registerFollowUpLogic('post', 'update', 'Pedido', validarPedido)


####################################################################################################
def removeEgreso(egreso):
    if egreso.resumen.upper() == 'MATERIA.PRIMA-FRUTA':
        for fruta in egreso.compras:
            ndb.Key(LoteDeCompra, fruta.detalle.upper() + '.' + egreso.proveedor.id() + '.' + str(egreso.fecha)).delete()

def postCreateEgreso(egreso):
    if egreso.resumen.upper() == 'MATERIA.PRIMA-FRUTA':
        for fruta in egreso.compras:
            values = {'fruta':ndb.Key(Fruta,fruta.detalle.upper()),
                      'proveedor': egreso.proveedor,
                      'fecha':egreso.fecha,
                      'precio':fruta.precio,
                      'peso':fruta.cantidad
                      }
            dataStoreInterface.create_entity('LoteDeCompra', values)

    

dataStoreInterface.registerFollowUpLogic('post','create','Egreso', postCreateEgreso)
dataStoreInterface.registerFollowUpLogic('pre','update','Egreso', removeEgreso)
dataStoreInterface.registerFollowUpLogic('post','update','Egreso', postCreateEgreso)
dataStoreInterface.registerFollowUpLogic('post','delete','Egreso', removeEgreso)

