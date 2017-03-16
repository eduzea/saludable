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

def updateUnidadDeAlamcenamiento(mi):
    ubicacion = mi.ubicacion
    keyStr = '.'.join([mi.fecha,mi.producto,mi.porcion])
    canastilla = UnidadDeAlmacenamiento.query(UnidadDeAlmacenamiento.ubicacion == ubicacion).fetch()[0]
    for fraccion in canastilla.contenido:
        pass


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

