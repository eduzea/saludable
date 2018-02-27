'''
Created on Jul 25, 2015

@author: eduze_000
'''
from myapp.model.models import *
from myapp.initSaludable import dataStoreInterface

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
    # First remove existing FDLU that refer to this ubicacacion
    ubicacion = unidadDeAlmacenamiento.key.id()
    entities = dataStoreInterface.buildQuery('FraccionDeLoteUbicado',{'ubicacion':ubicacion}).fetch()
    for entity in entities:
        entity.key.delete()
    # Then create the new ones
    for fraccionDeLote in unidadDeAlmacenamiento.contenido:
        values = fraccionDeLote.to_dict()
        values['ubicacion'] =  unidadDeAlmacenamiento.key.id()
        flu = dataStoreInterface.create_entity('FraccionDeLoteUbicado',values)['entity'] 
        flu.put()

dataStoreInterface.registerFollowUpLogic('post', 'create', 'UnidadDeAlmacenamiento', updateFraccionDeLote)
dataStoreInterface.registerFollowUpLogic('post', 'update', 'UnidadDeAlmacenamiento', updateFraccionDeLote)

def removeFraccionDeLoteUbicado(fdl,ubicacion):
    values = fdl.to_dict()
    params = {'ubicacion':ubicacion,'fecha':values['fecha'],'producto':values['producto'], 'porcion':values['porcion']}
    entities = dataStoreInterface.buildQuery('FraccionDeLoteUbicado',params).fetch()
    for entity in entities:
        entity.key.delete()


        

def updateUnidadDeAlamcenamiento(mi):
    ubicacion = mi.ubicacion
    canastilla = UnidadDeAlmacenamiento.query(UnidadDeAlmacenamiento.key == ubicacion).fetch()[0]
    presente = False
    loteKey = '{0}.{1}.{2}'.format(mi.fechaLote, mi.producto.id(), mi.porcion.id())
    for idx,fdl in enumerate(canastilla.contenido):
        if fdl.rotulo == loteKey: #lote is in canastilla
            presente = True
            tipo = -1 if mi.tipo.name == 'SALIDA' else 1
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

def rollbackMovimientoDeInventario(mi):
    ubicacion = mi.ubicacion
    canastilla = UnidadDeAlmacenamiento.query(UnidadDeAlmacenamiento.key == ubicacion).fetch()[0]
    presente = False
    loteKey = '{0}.{1}.{2}'.format(mi.fechaLote, mi.producto.id(), mi.porcion.id())
    for idx,fdl in enumerate(canastilla.contenido):
        if fdl.rotulo == loteKey: #lote is in canastilla
            presente = True
            tipo = 1 if mi.tipo.id() == 'SALIDA' else -1
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



dataStoreInterface.registerFollowUpLogic('post', 'create', 'MovimientoDeInventario', updateUnidadDeAlamcenamiento)
dataStoreInterface.registerFollowUpLogic('post', 'update', 'MovimientoDeInventario', updateUnidadDeAlamcenamiento)
dataStoreInterface.registerFollowUpLogic('post', 'delete', 'MovimientoDeInventario', rollbackMovimientoDeInventario)

################# PEDIDOS ####################################
                    
def crearMovimientoDeInventario(fdl, tipo, cantidad):
    params = {'fecha' : datetime.today(),
              'ubicacion' : fdl.ubicacion,
              'tipo' : tipo,
              'fechaLote' : fdl.fecha,
              'producto' : fdl.producto,
              'porcion' : fdl.porcion,
              'cantidad' : cantidad}
    return dataStoreInterface.create_entity('MovimientoDeInventario', params)['entity']
            
####################!!!! incomplete


#dataStoreInterface.registerFollowUpLogic('post', 'create', 'Pedido', validarPedido)
#dataStoreInterface.registerFollowUpLogic('post', 'update', 'Pedido', validarPedido)
#######################################################
def postCreateProduccion(produccion):
    for comp in produccion.componentes:
        compra = comp.lote.get()
        compra.procesado = True
        compra.put()
    
dataStoreInterface.registerFollowUpLogic('post', 'create', 'Produccion', postCreateProduccion)
####################################################################################################
def removeEgreso(egreso):
    compras = dataStoreInterface.buildQuery('Compra', {'egreso':egreso.numero} ).fetch()
    for compra in compras:
        dataStoreInterface.deleteEntity('Compra', compra)

dataStoreInterface.registerFollowUpLogic('pre','update','Egreso', removeEgreso)
dataStoreInterface.registerFollowUpLogic('post','delete','Egreso', removeEgreso)

