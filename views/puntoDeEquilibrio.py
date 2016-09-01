'''
Created on Aug 29, 2016

@author: eduze_000
'''
from easydict import EasyDict as edict
from datastorelogic import DataStoreInterface

############# Init the instance! ################# There's probably a better way!
if 'dataStoreInterface' not in globals():
    dataStoreInterface = DataStoreInterface()

##################### FORMULAS PUNTO DE EQUILIBRIO ##################################

# This function assumes the queried entities have a 'total' field
def getTotalFromModel(model, qryParams):
    query = dataStoreInterface.buildQuery(model, qryParams)
    entities = query.fetch()
    if entities:
        return sum([entity.total for entity in entities])
    else:
        return 0

def getVentasNetas(fechaDesde, fechaHasta):
    ventasPyG = getTotalFromModel('Factura', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta})
    devoluciones = getTotalFromModel('Devolucion', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta})
    return ventasPyG - devoluciones

def getCostosFijos(fechaDesde, fechaHasta):
    costosDeProduccion = [  'ARRIENDO',
                            'NOMINA-TURNOS',
                            'SERVICIOS.PUBLICOS-ENERGIA',
                            'NOMINA.-.OPERATIVA',
                            'ALIMENTACION.EMPLEADO',
                            'SERVICIOS.PUBLICOS-AGUA',
                            'APORTES.PENSION',
                            'SERVICIOS.PUBLICOS-GAS',
                            'MATERIA.PRIMA-IMPLEMENTOS.DE.ASEO',
                            'UTENSILIOS',
                            'DOTACION.EMPLEADOS',
                            'MANTENIMIENTO.DE.VEHICULOS',
                            'APORTES.EPS',
                            'APORTES.CAJA.DE.COMPENSACION',
                            'DOTACION',
                            'APORTES.ARL']
    
    gastosDeAdminVentas = [ 'NOMINA.-.ADMINISTRATIVA',
                            'PAPELERIA',
                            'SERVICIOS.PUBLICOS-TELECOMUNICACIONES',
                            'VIGILANCIA',
                            'PRUEBAS.LABORATORIO',
                            'PUBLICIDAD',
                            'SERVICIOS-FUMIGACION',
                            'CURSOS.PARA.EL.PERSONAL',
                            'MEDICINAS.BOTIQUIN',
                            'PARQUEADERO',
                            'CAMARA.DE.COMERCIO']

    
    costos = getTotalFromModel('Egreso', {'resumen':costosDeProduccion,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    gastos = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentas,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    return costos + gastos
    
def getCostosVariables(fechaDesde, fechaHasta):
    costosDeProduccion = [  'MATERIA.PRIMA-FRUTA',
                            'MATERIA.PRIMA-BOLSAS.PLASTICAS',
                            'MATERIA.PRIMA-VARIOS',
                            'MATERIA.PRIMA-QUIMICOS',
                            'PLASTICOS',
                            'MATERIA.PRIMA-HIELO.SECO'
                            ]
    
    gastosDeAdminVentas = ['TRANSPORTE.DEL.PRODUCTO-INTERMUNICIPAL',
                            'TAXIS.Y.PASAJES.DE.BUS',
                            'COMBUSTIBLE',
                            'PAGO.DE.DEUDA',
                            'SERVICIOS-VARIOS',
                            'HONORARIOS',
                            'TRANSPORTE.DEL.PRODUCTO-LOCAL',
                            'IMPUESTO.DE.INDUSTRIA.Y.COMERCIO',
                            'PASAJES.AEREOS',
                            'IMPUESTO.-.RENTA',
                            'IMPUESTO.-.IVA',
                            'SERVICIOS.FINANCIEROS',
                            'GASTOS.EXTRAORDINARIOS'
                           ]
    
    costos = getTotalFromModel('Egreso', {'resumen':costosDeProduccion,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    gastos = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentas,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    return costos + gastos

def getUtilidadBruta(fechaDesde, fechaHasta):
    return getVentasNetas(fechaDesde, fechaHasta) - getCostosVariables(fechaDesde, fechaHasta)

def getUtilidadNeta(fechaDesde, fechaHasta):
    return getUtilidadBruta(fechaDesde, fechaHasta)-getCostosFijos(fechaDesde, fechaHasta)

def getMargenBruto(fechaDesde, fechaHasta):
    return 100 * getUtilidadBruta(fechaDesde, fechaHasta) / getVentasNetas(fechaDesde, fechaHasta)

def getMargenNeto(fechaDesde, fechaHasta):
    return 100 * getUtilidadNeta(fechaDesde, fechaHasta) / getVentasNetas(fechaDesde, fechaHasta)

def getUtilidadData(fechaDesde, fechaHasta):
    ventas = getVentasNetas(fechaDesde, fechaHasta)
    costosVariables = getCostosVariables(fechaDesde, fechaHasta)
    costosFijos = getCostosFijos(fechaDesde, fechaHasta)
    utilidadBruta = ventas - costosVariables
    utilidadNeta = utilidadBruta - costosFijos
    utilidadData =  {   'ventas' : ventas,
                        'costosVariables' : costosVariables,
                        'costosFijos' : costosFijos,
                        'utilidadBruta' : utilidadBruta,
                        'utilidadNeta' : utilidadNeta,
                        'margenBruto' : 1.0 * utilidadBruta / ventas,
                        'margenNeto' : 1.0 * utilidadNeta / ventas}
    return utilidadData

