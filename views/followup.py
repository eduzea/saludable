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
        factura.abono = 0
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
            if factura.total-factura.abono <= pagado:
                pagado = pagado - factura.total-factura.abono
                factura.pagada = True
                factura.pagoRef = pago.numero
                factura.put()
            else:
                factura.abono += pagado
                factura.pagoRef = pago.numero
                factura.put()
                break
    elif response['message'] == 'Updated':
        removePayment(pago)
        updateCuentasPorCobrar({'entity':pago, 'message':'Created'})
    else:
        removePayment(pago)
            
        
postSaveAction['PagoRecibido'] = updateCuentasPorCobrar
postDeleteAction['PagoRecibido'] = updateCuentasPorCobrar
