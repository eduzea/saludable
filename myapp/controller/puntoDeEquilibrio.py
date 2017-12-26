'''
Created on Aug 29, 2016

@author: eduze_000
'''
from easydict import EasyDict as edict
from myapp.initSaludable import dataStoreInterface


##################### FORMULAS PUNTO DE EQUILIBRIO ##################################

def getDetailFromModel(model,qryParams):
    query = dataStoreInterface.buildQuery(model, qryParams)
    return query.fetch()


# This function assumes the queried entities have a 'total' field
def getTotalFromModel(model, qryParams):
    query = dataStoreInterface.buildQuery(model, qryParams)
    entities = query.fetch()
    return edict({'total': sum([entity.total for entity in entities]), 'data':entities })

def getIngresosOperacionales(fechaDesde, fechaHasta):
    ventasPyG = getTotalFromModel('Factura', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta}).total
    devoluciones = getTotalFromModel('Devolucion', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta}).total
    return ventasPyG - devoluciones

def getCostosDeProduccion(fechaDesde, fechaHasta):
    bos = dataStoreInterface.buildQuery('Bienoservicio', {'clase':'7'}).fetch()
    return getTotalFromModel('Compra', {'bienoservicio':bos,
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta': fechaHasta}).total

def getGastosOperacionales(fechaDesde, fechaHasta):
    bos = dataStoreInterface.buildQuery('Bienoservicio', {'grupo':['51','52']}).fetch()
    costos = getTotalFromModel('Compra', {'bienoservicio':bos,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta}).total
    return costos

                                         
def getGastosNoOperacionales(fechaDesde, fechaHasta):
    bos = dataStoreInterface.buildQuery('Bienoservicio', {'grupo':'53'}).fetch()
    return getTotalFromModel('Compra', {'bienoservicio':bos,
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta': fechaHasta}).total

def getImpuestos(fechaDesde, fechaHasta):
    bos = dataStoreInterface.buildQuery('Bienoservicio', {'grupo':'54'}).fetch()
    return getTotalFromModel('Compra', {'bienoservicio':bos,
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta': fechaHasta}).total

def getDividendos(fechaDesde, fechaHasta):
    return getTotalFromModel('Pasivo', {'cuenta':'2360','fechaDesde':fechaDesde,'fechaHasta': fechaHasta}).total


def estadoDeResultados(fechaDesde, fechaHasta):
    ingresosOperacionales = getIngresosOperacionales(fechaDesde, fechaHasta)
    costosDeProduccion = getCostosDeProduccion(fechaDesde, fechaHasta)
    utilidadOperacionalBruta = ingresosOperacionales - costosDeProduccion
    gastosOperacionales = getGastosOperacionales(fechaDesde, fechaHasta)
    utilidadOperacionalNeta = utilidadOperacionalBruta - gastosOperacionales
    gastosNoOperacionales = getGastosNoOperacionales(fechaDesde, fechaHasta)
    utilidadAntesDeImpuestos = utilidadOperacionalNeta - gastosNoOperacionales
    impuestos = getImpuestos(fechaDesde, fechaHasta)
    utilidadNeta = utilidadAntesDeImpuestos - impuestos
    pagoDeDividendos = getDividendos(fechaDesde, fechaHasta)
    utilidadRetenida = utilidadNeta - pagoDeDividendos
    estadoDeResultadosData =[  
        {'id':'Ingresos Operacionales','cuenta':'Ingresos Operacionales', 'monto': ingresosOperacionales},
        {'id':'Costos de Produccion','cuenta':'Costos de Produccion', 'monto': costosDeProduccion},
        {'id':'Utilidad Operacional Bruta','cuenta':'Utilidad Operacional Bruta', 'monto': utilidadOperacionalBruta},
        {'id':'Margen Operacional Bruto','cuenta':'Margen Operacional Bruto', 'monto':1.0 * utilidadOperacionalBruta / ingresosOperacionales },
        {'id':'Gastos Operacionales','cuenta':'Gastos Operacionales', 'monto': gastosOperacionales},
        {'id':'Utilidad Operacional Neta','cuenta':'Utilidad Operacional Neta', 'monto': utilidadOperacionalNeta},
        {'id':'Margen Operacional Neto','cuenta':'Margen Operacional Neto', 'monto':1.0 * utilidadOperacionalNeta / ingresosOperacionales },
        {'id':'Gastos No Operacionales','cuenta':'Gastos No Operacionales', 'monto': gastosNoOperacionales},
        {'id':'Utilidad Antes de Impuestos','cuenta':'Utilidad Antes de Impuestos', 'monto': utilidadAntesDeImpuestos},
        {'id':'Impuestos','cuenta':'Impuestos', 'monto': impuestos},
        {'id':'Utilidad Neta','cuenta':'Utilidad Neta', 'monto': utilidadNeta},
        {'id':'Pago de Dividendos','cuenta':'Pago de Dividendos', 'monto': pagoDeDividendos},
        {'id':'Utilidad Retenida','cuenta':'Utilidad Retenida', 'monto': utilidadRetenida}
    ]    
    return estadoDeResultadosData

def detalleEstadoDeResultados(cuenta,fechaDesde, fechaHasta):
    if cuenta == 'Ingresos Operacionales':
        return getDetailFromModel('Factura', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta})
    elif cuenta == 'Costos de Produccion':
        bos = dataStoreInterface.buildQuery('Bienoservicio', {'clase':'7'}).fetch()
        return getDetailFromModel('Compra', {'bienoservicio':bos,
                                            'fechaDesde':fechaDesde,
                                            'fechaHasta': fechaHasta})
    elif cuenta == 'Gastos Operacionales':
        bos = dataStoreInterface.buildQuery('Bienoservicio', {'grupo':['51','52']}).fetch()
        return getDetailFromModel('Compra', {'bienoservicio':bos,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    elif cuenta == 'Gastos No Operacionales':
        bos = dataStoreInterface.buildQuery('Bienoservicio', {'grupo':'53'}).fetch()
        return getDetailFromModel('Compra', {'bienoservicio':bos,
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta': fechaHasta})
    elif cuenta == 'Impuestos':
        bos = dataStoreInterface.buildQuery('Bienoservicio', {'grupo':'54'}).fetch()
        return getDetailFromModel('Compra', {'bienoservicio':bos,
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta': fechaHasta})   
    elif cuenta == 'Pago de Dividendos':
        return getDetailFromModel('Pasivo', {'cuenta':'2360',
                                             'fechaDesde':fechaDesde,
                                             'fechaHasta': fechaHasta}).total
# def getUtilidadData(fechaDesde, fechaHasta):
#     ventas = getVentasNetas(fechaDesde, fechaHasta)
#     costosVariables = getCostosVariables(fechaDesde, fechaHasta)
#     costosFijos = getCostosFijos(fechaDesde, fechaHasta)
#     utilidadBruta = ventas - costosVariables
#     utilidadNeta = utilidadBruta - costosFijos
#     utilidadData =  {   'ventas' : ventas,
#                         'costosVariables' : costosVariables,
#                         'costosFijos' : costosFijos,
#                         'utilidadBruta' : utilidadBruta,
#                         'utilidadNeta' : utilidadNeta,
#                         'margenBruto' : 1.0 * utilidadBruta / ventas,
#                         'margenNeto' : 1.0 * utilidadNeta / ventas}
#     return utilidadData

# def getUtilidadDataFull(fechaDesde, fechaHasta):
#     registros = []
#     ventas = getTotalFromModel('Factura', {'fechaDesde':fechaDesde, 'fechaHasta': fechaHasta})
#     costosVariables = getTotalFromModel('Egreso', {'resumen':costosDeProduccionVariables,
#                                                  'fechaDesde':fechaDesde,
#                                                  'fechaHasta': fechaHasta})
#     gastosVariables = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentasVariables,
#                                                  'fechaDesde':fechaDesde,
#                                                  'fechaHasta': fechaHasta})
#     costosFijos = getTotalFromModel('Egreso', {'resumen':costosDeProduccionFijos,
#                                                  'fechaDesde':fechaDesde,
#                                                  'fechaHasta': fechaHasta})
#     gastosFijos = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentasFijos,
#                                                  'fechaDesde':fechaDesde,
#                                                  'fechaHasta': fechaHasta}) 
#     
#     monthData = {'Ventas':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
#                  'Costos Variables':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
#                  'Gastos Variables':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
#                  'Costos Fijos':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
#                  'Gastos Fijos':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0} }
#     
#     for factura in ventas.data:
#         registros.append({'tipo':'Ventas', 'sortRows':1 ,'detalle':factura.cliente.id(),'mesnum':factura.fecha.month,'mes': calendar.month_abbr[factura.fecha.month],'total':factura.total})
#         monthData['Ventas'][factura.fecha.month] += factura.total
#     
#     for egreso in costosVariables.data:
#         registros.append({'tipo':'Costos Variables', 'sortRows':2 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month],'total':egreso.total})
#         monthData['Costos Variables'][egreso.fecha.month] += egreso.total
#         
#     for egreso in gastosVariables.data:
#         registros.append({'tipo':'Gastos Variables', 'sortRows':3 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month],'total':egreso.total})
#         monthData['Gastos Variables'][egreso.fecha.month] += egreso.total
#         
#     for egreso in costosFijos.data:
#         registros.append({'tipo':'Costos Fijos', 'sortRows':6 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month], 'total':egreso.total})
#         monthData['Costos Fijos'][egreso.fecha.month] += egreso.total
#      
#     for egreso in gastosFijos.data:
#         registros.append({'tipo':'Gastos Fijos', 'sortRows':7 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month], 'total':egreso.total})    
#         monthData['Gastos Fijos'][egreso.fecha.month] += egreso.total
#     
#     utilidadBruta=[]
#     margenBruto = []
#     utilidadNeta =[]
#     margenNeto = []
#     maxMonth = date.today().month
#     for month in range(1, maxMonth+1):
#         try:
#             utilidadBruta.append(monthData['Ventas'][month] - monthData['Costos Variables'][month] - monthData['Gastos Variables'][month])
#             utilidadNeta.append(utilidadBruta[month-1] - monthData['Costos Fijos'][month] - monthData['Gastos Fijos'][month])
#             margenBruto.append(100.0 * utilidadBruta[month-1] / monthData['Ventas'][month])
#             margenNeto.append(100.0 * utilidadNeta[month-1] / monthData['Ventas'][month])
#             registros.append({'tipo':'Utilidad Bruta','sortRows':4,'detalle':'Utilidad Bruta','mesnum':month,'mes': calendar.month_abbr[month],'total': utilidadBruta[month-1]})
#             registros.append({'tipo':'Margen Bruto(%)','sortRows':5,'detalle':'Margen Bruto','mesnum':month,'mes': calendar.month_abbr[month],'total':margenBruto[month-1]})
#             registros.append({'tipo':'Utilidad Neta','sortRows':8,'detalle':'Utilidad Neta','mesnum':month,'mes': calendar.month_abbr[month],'total':utilidadNeta[month-1]})
#             registros.append({'tipo':'Margen Neto(%)','sortRows':9,'detalle':'Margen Neto','mesnum':month,'mes': calendar.month_abbr[month],'total':margenNeto[month-1]})
#         except:
#             print month, ", ", maxMonth
#     return registros

