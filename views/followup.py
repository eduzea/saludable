'''
Created on Jul 25, 2015

@author: eduze_000
'''
from models.models import *
from datetime import datetime, date, time
from datastorelogic import create_entity

preSaveAction = {}
postSaveAction ={}
postDeleteAction={}

####################### PAGO RECIBIDO Y CUENTAS POR COBRAR ###################################
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


def updateCuentasPorCobrar(pago):
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

preSaveAction['PagoRecibido'] = removePayment
postSaveAction['PagoRecibido'] = updateCuentasPorCobrar
postDeleteAction['PagoRecibido'] = removePayment

######################### FACTURA Y EXISTENCIAS ##############################
def removeFactura(factura):
    sucursal = factura.cliente.get().sucursal
    existencias = Existencias.query(Existencias.sucursal == sucursal).fetch()
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
    sucursal = factura.cliente.get().sucursal
    existencias = Existencias.query(Existencias.sucursal == sucursal).fetch()
    if existencias:
        existencias = existencias[0]
        indexMap = {x.id():i for i,x in enumerate(existencias.registros)}
        for venta in factura.ventas:
            ventaKey = sucursal.id() + '.' + venta.producto.id() + '.' + venta.porcion.id() 
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

######################### INVENTARIO Y EXISTENCIAS ################################

def actualizarExistencias(inventario):
    existencias = Existencias.query(Existencias.sucursal == inventario.sucursal).fetch()
    if not existencias:
        registros = []
        for registro in inventario.registros:
            existenciaRegistro = create_entity('ExistenciasRegistro',registro.get().to_dict())['entity']#cloning record
            existenciaRegistro.put()
            registros.append(existenciaRegistro.key)
        existencias = create_entity('Existencias', { 
                                  'sucursal': inventario.sucursal,
                                  'fecha' : datetime.today(),
                                  'registros' : registros,
                                  'ultimoInventario' : inventario.key,
                                  'ultimasFacturas' : []}
                                  )['entity']
        existencias.put()
        return
    else:
        existencias = existencias[0]
        indexMap = {x.id():i for i,x in enumerate(existencias.registros)}
        for registro in inventario.registros:
            registroKey = registro.id().partition('.')[2]   
            if  registroKey in indexMap:
                index = indexMap[registroKey]
                productoPorcion = existencias.registros[index].get()
                productoPorcion.existencias = registro.get().existencias
                productoPorcion.put()
            else:
                registro = registro.get()
                nuevoRegistro  = create_entity('ExistenciasRegistro',
                                               {'fecha':registro.fecha,                                                                        
                                                'sucursal': registro.sucursal,
                                                'producto': registro.producto,
                                                'porcion':  registro.porcion,
                                                'existencias':  registro.existencias})['entity']
                existencias.registros.append(nuevoRegistro.key)
        existencias.put()

def actualizarInventarioRegistros(inventario):
    for registro in inventario.registros:
        registro.delete()
        
postSaveAction['Inventario'] = actualizarExistencias
postDeleteAction['Inventario'] = actualizarInventarioRegistros

######################### PRODUCCION Y EXISTENCIAS ##########################

def sumarExistencias(produccion):
    sucursal = produccion.sucursal
    producto = produccion.producto
    existencias = Existencias.query(Existencias.sucursal == sucursal).fetch()
    if existencias:
        existencias = existencias[0]
        indexMap = {x.id():i for i,x in enumerate(existencias.registros)}
        for productoPorcion in produccion.productos:
            key = sucursal.id() + '.' + producto.id() + '.' + productoPorcion.porcion.id() 
            if key in indexMap:
                index = indexMap[key]
                existenciasProductoPorcion = existencias.registros[index].get()
                existenciasProductoPorcion.existencias += productoPorcion.cantidad
                existenciasProductoPorcion.put()
            else:
                nuevoRegistro  = create_entity('ExistenciasRegistro',
                                               {'fecha':produccion.fecha,                                                                        
                                                'sucursal': sucursal,
                                                'producto': producto,
                                                'porcion':  productoPorcion.porcion,
                                                'existencias':  productoPorcion.existencias})['entity']
                existencias.registros.append(nuevoRegistro.key)
        existencias.put()
        
def removeProduccion(produccion):
    sucursal = produccion.sucursal
    producto = produccion.producto
    existencias = Existencias.query(Existencias.sucursal == sucursal).fetch()
    if existencias:
        existencias = existencias[0]#This function assumes that Existencias for every city exist in the Datastore
        indexMap = {x.id():i for i,x in enumerate(existencias.registros)}
        for productoPorcion in produccion.productos:
            key = sucursal.id() + '.' + producto.id() + '.' + productoPorcion.porcion.id() 
            if key in indexMap:
                index = indexMap[key]
                existenciasProductoPorcion = existencias.registros[index].get()
                existenciasProductoPorcion.existencias -= productoPorcion.cantidad
                existenciasProductoPorcion.put()
        existencias.put()

preSaveAction['Produccion'] = removeProduccion
postSaveAction['Produccion'] = sumarExistencias
postDeleteAction['Produccion']=removeProduccion


