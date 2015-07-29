'''
Created on Jul 25, 2015

@author: eduze_000
'''
from models.models import *

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
    for venta in factura.ventas:    
        registro = Inventario.query(Inventario.ciudad == factura.ciudad,
                                        Inventario.producto == venta.producto,
                                        Inventario.porcion == venta.porcion ).fetch()
        if registro:
            registro.existencia += venta.cantidad
            registro.put()


def updateInventario(response):
    factura = response['entity']
    if response['message'] == 'Created':
        ciudad = factura.ciudad
        for venta in factura.ventas:
            registro = Inventario.query(Inventario.ciudad == ciudad,
                                        Inventario.producto == venta.producto,
                                        Inventario.porcion == venta.porcion ).fetch()
            if registro:
                registro.existencia -= venta.cantidad
                registro.put()
    elif response['message'] == 'Updated':
        removeFactura(factura)
        updateInventario({'entity':factura, 'message':'Created'})
    else:
        removeFactura(factura)

postSaveAction['Factura'] = updateInventario
postDeleteAction['Factura'] = updateInventario

def removeEntradaInventario(entrada):
    registro = Inventario.query(Inventario.ciudad == entrada.ciudad,
                                        Inventario.producto == entrada.producto,
                                        Inventario.porcion == entrada.porcion ).fetch()
    if registro:
            registro.existencia -= entrada.cantidad
            registro.put()

def sumarInventario(response):
    entrada = response['entity']
    if response['message'] == 'Created':
        registro = Inventario.query(Inventario.ciudad == entrada.ciudad,
                                        Inventario.producto == entrada.producto,
                                        Inventario.porcion == entrada.porcion ).fetch()
        if registro:
            registro.existencia += entrada.existencias
            registro.put()
    elif response['message'] == 'Updated':
        removeEntradaInventario(entrada)
        sumarInventario({'entity':entrada, 'message':'Updated'})
    else:
        removeEntradaInventario(entrada)
        
postSaveAction['InventarioRegistro'] = sumarInventario
postDeleteAction['InventarioRegistro'] = sumarInventario

