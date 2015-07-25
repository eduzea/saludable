'''
Created on Jul 25, 2015

@author: eduze_000
'''
from models.models import *

postSaveAction ={}

def updateCuentasPorCobrar(pago):
    cliente = pago.cliente
    pagado = pago.monto
    facturasImpagas = Factura.query(Factura.pagada == False, Factura.cliente == cliente).fetch()
    facturasImpagas.sort(key=lambda factura: factura.numero)
    for factura in facturasImpagas:
        if factura.total-factura.abono <= pagado:
            pagado = pagado - factura.total-factura.abono
            factura.pagada = True
            factura.put()
        else:
            factura.abono += pagado
            factura.put()

postSaveAction['PagoRecibido'] = updateCuentasPorCobrar
