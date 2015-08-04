'''
Created on Jul 25, 2015

@author: eduze_000
'''
from models.models import *
from datetime import datetime, date, time

preSaveAction = {}
postSaveAction ={}
postDeleteAction={}

def removePayment(pago):
    facturasAjustadas = Factura.query(Factura.pagoRef == pago.numero).fetch()
    facturasAjustadas.sort(key=lambda factura: factura.numero)
    for factura in facturasAjustadas:
        factura.pagada = False
        index = factura.pagoRef.index(pago.numero)
        factura.pagoRef.remove(pago.numero)
        if factura.abono:
            del factura.abono[index]
        factura.put()          


def updateCuentasPorCobrar(response):
    pago = response['entity']
    if response['message'] == 'Created':
        cliente = pago.cliente
        pagado = pago.monto
        clienteNegocios = Cliente.query(Cliente.nombre == cliente.get().nombre).fetch()
        facturasImpagas = []
        for negocio in clienteNegocios: 
            facturas = Factura.query(Factura.pagada == False, Factura.cliente == negocio.key).fetch()
            facturasImpagas.extend(facturas)
        facturasImpagas.sort(key=lambda factura: factura.numero)
        for factura in facturasImpagas:
            if ( factura.total-sum(factura.abono) ) <= pagado:
                pagado = pagado - ( factura.total- sum(factura.abono) )
                factura.pagada = True
                factura.pagoRef.append(pago.numero)
                factura.abono.append(pagado)
                factura.put()
            else:
                factura.abono.append(pagado)
                factura.pagoRef.append(pago.numero)
                factura.put()
                break
    elif response['message'] == 'Updated':
        removePayment(pago)
        updateCuentasPorCobrar({'entity':pago, 'message':'Created'})
    else:
        removePayment(pago)

postSaveAction['PagoRecibido'] = updateCuentasPorCobrar
postDeleteAction['PagoRecibido'] = updateCuentasPorCobrar
            
def removeFactura(factura):
    ciudad = factura.cliente.get().ciudad
    existencias = Existencias.query(Existencias.ciudad == ciudad).fetch()
    if existencias:
        existencias = existencias[0]#This function assumes that Existencias for every city exist in the Datastore
        indexMap = {x.id():i for i,x in enumerate(existencias.registros)}
        for venta in factura.ventas:
            ventaKey = venta.producto.id() + '.' + venta.porcion.id()    
            if ventaKey in indexMap:
                index = indexMap[ventaKey]
                productoPorcion = existencias.registros[index].get()
                productoPorcion.existencias += venta.cantidad
                productoPorcion.put()
            else:
                print "UN PRODUCTO QUE NO HAY EN EXISTENCIAS!"
        existencias.put()


def restarExistencias(factura):
    ciudad = factura.cliente.get().ciudad
    existencias = Existencias.query(Existencias.ciudad == ciudad).fetch()
    if existencias:
        existencias = existencias[0]
        indexMap = {x.id():i for i,x in enumerate(existencias.registros)}
        for venta in factura.ventas:
            ventaKey = venta.producto.id() + '.' + venta.porcion.id() 
            if ventaKey in indexMap:
                index = indexMap[ventaKey]
                productoPorcion = existencias.registros[index].get()
                if productoPorcion.existencias >= venta.cantidad:
                    productoPorcion.existencias -= venta.cantidad
                    productoPorcion.put()
                else:
                    print "NO ALCANZA!" 
            else:
                print "UN PRODUCTO QUE NO HAY EN EXISTENCIAS!"
        existencias.put()

preSaveAction['Factura'] = removeFactura
postSaveAction['Factura'] = restarExistencias
postDeleteAction['Factura'] = removeFactura

def actualizarExistencias(response):
    inventario = response['entity']
    existencias = Existencias.query(Existencias.ciudad == inventario.ciudad).fetch()
    if not existencias:
        existencias = Existencias(id = str(datetime.today()) + '.' + inventario.ciudad.id(), 
                                  ciudad = inventario.ciudad,
                                  fecha = datetime.today(),
                                  registros = inventario.registros,
                                  ultimoInventario = inventario.key,
                                  ultimasFacturas = []
                                  )
        existencias.put()
        return
    else:
        existencias = existencias[0]
        indexMap = {x.id():i for i,x in enumerate(existencias.registros)}
        for registro in inventario.registros:
            if registro.id() in indexMap:
                index = indexMap[registro.id()]
                productoPorcion = existencias.registros[index].get()
                productoPorcion.existencias = registro.get().existencias
                productoPorcion.put()
            else:
                registro = registro.get()
                nuevoRegistro  = InventarioRegistro(id = registro.producto.id() + "." + registro.porcion.id(),
                                             fecha = registro.fecha,
                                             ciudad = registro.ciudad,
                                             producto = registro.producto,
                                             porcion = registro.porcion,
                                             existencias = registro.existencias)
                nuevoRegistro.put()
                existencias.registros.append(nuevoRegistro.key)
        existencias.put()
        
postSaveAction['Inventario'] = actualizarExistencias

