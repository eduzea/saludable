'''
Created on Aug 29, 2016

@author: eduze_000
'''
from easydict import EasyDict as edict
from myapp.initSaludable import dataStoreInterface
from myapp.model.models import AnticipoImpuestos


##################### FORMULAS PUNTO DE EQUILIBRIO ##################################

def getDetailFromModel(model,qryParams):
    query = dataStoreInterface.buildQuery(model, qryParams)
    return query.fetch()


# This function assumes the queried entities have a 'total' field
def getTotalFromModel(model, qryParams):
    query = dataStoreInterface.buildQuery(model, qryParams)
    entities = query.fetch()
    return edict({'total': sum([entity.total for entity in entities]), 'data':entities })

# Functions for Estado de resultados #

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


# Functions fro Balance
def getActivoDisponible(fechaDesde, fechaHasta):
    """"
    Activo Disponible = Caja  + Bancos
    """
    cuentas = dataStoreInterface.buildQuery('CuentaBancaria',{}).fetch()
    caja = 0
    saldo = 0
    for cuenta in cuentas:
        saldoObj = dataStoreInterface.buildQuery('SaldoCuentaBancaria',{'cuenta':cuenta.key,'fechaHasta':fechaHasta,'sortBy':'-fecha'}).fetch(1)[0]
        saldo += saldoObj.saldo
    return caja + saldo 

def getDeudores(fechaDesde, fechaHasta):
    carteraClientes = getTotalFromModel('Factura', {'pagada':False,
                                                    'fechaDesde':fechaDesde,
                                                    'fechaHasta':fechaHasta})
    anticipoImpuestosContribucionesSaldosAfavor = 0
    return carteraClientes.total + anticipoImpuestosContribucionesSaldosAfavor

def getPrice(producto, porcion):
    precios = dataStoreInterface.buildQuery('Precio', {'producto':producto,
                                                       'porcion':porcion}).fetch()
    return sum(precio.precio for precio in precios)/max(len(precios), 1)

def getInventarios(fechaDesde, fechaHasta):
    records = dataStoreInterface.buildQuery('FraccionDeLoteUbicado', {'fechaDesde':fechaDesde,
                                                             'fechaHasta':fechaHasta}).fetch()
    sumInventario = 0
    for record in records:
        price = getPrice(record.producto, record.porcion)
        sumInventario = record.cantidad * price
    return sumInventario
                                             
def balance(fechaDesde, fechaHasta):
    activoDisponible = getActivoDisponible(fechaDesde, fechaHasta)
    deudores = getDeudores(fechaDesde, fechaHasta)
    inventarios = getInventarios(fechaDesde, fechaHasta)
#     propiedadPlantaEquipo = getPropiedadPlantaEquipo(fechaDesde, fechaHasta)
#     depreciacionAcumulada = getDepreciacionAcumulada(fechaDesde, fechaHasta)
#     intangibles = getIntangibles(fechaDesde, fechaHasta)
#     diferidos = getDiferidos(fechaDesde, fechaHasta)
#     totalActivo = activoDisponible + deudores + inventarios + propiedadPlantaEquipo + depreciacionAcumulada + intangibles + diferidos
#     
#     pasivoCorriente = getPasivoCorriente(fechaDesde, fechaHasta)
#     pasivoNoCorriente = getPasivoNoCorriente(fechaDesde, fechaHasta)
#     proveedores = getProveedores(fechaDesde, fechaHasta)
#     impuestosGravamenesTasas = getImpuestosGravamenesTasas(fechaDesde, fechaHasta)
#     otrosPasivos = getOtrosPasivos(fechaDesde, fechaHasta)
#     totalPasivo = pasivoCorriente + pasivoNoCorriente + proveedores + impuestosGravamenesTasas + otrosPasivos
#     
#     aportesSociales = getAportesSociales(fechaDesde, fechaHasta)
#     resultadoDelEjercicio = getResultadoDelEjercicio(fechaDesde, fechaHasta)
#     resultadoEjerciciosAnteriores = getResultadoEjerciciosAnteriores(fechaDesde, fechaHasta)
#     totalPatrimonio = aportesSociales + resultadoDelEjercicio + resultadoEjerciciosAnteriores
#     totalPasivoPatrimonio = totalPasivo + totalPatrimonio
#  
    balanceData =[  
        {'id':'activoDisponible','cuenta':'Activo Disponible', 'monto': activoDisponible},
        {'id':'deudores','cuenta':'Deudores', 'monto': deudores},
        {'id':'inventarios','cuenta':'Inventarios', 'monto': inventarios},
#         {'id':'propiedadPlantaEquipo','cuenta':'Margen Operacional Bruto', 'monto': propiedadPlantaEquipo},
#         {'id':'depreciacionAcumulada','cuenta':'Gastos Operacionales', 'monto': depreciacionAcumulada},
#         {'id':'intangibles','cuenta':'Utilidad Operacional Neta', 'monto': intangibles},
#         {'id':'diferidos','cuenta':'Margen Operacional Neto', 'monto':diferidos},
#         {'id':'totalActivo','cuenta':'Gastos No Operacionales', 'monto': totalActivo},
#         {'id':'pasivoCorriente','cuenta':'Utilidad Antes de Impuestos', 'monto': pasivoCorriente},
#         {'id':'pasivoNoCorriente','cuenta':'Impuestos', 'monto': pasivoNoCorriente},
#         {'id':'proveedores','cuenta':'Utilidad Neta', 'monto': proveedores},
#         {'id':'impuestosGravamenesTasas','cuenta':'Pago de Dividendos', 'monto': impuestosGravamenesTasas},
#         {'id':'otrosPasivos','cuenta':'Utilidad Retenida', 'monto': otrosPasivos},
#         {'id':'totalPasivo','cuenta':'Utilidad Retenida', 'monto': totalPasivo},
#         {'id':'aportesSociales','cuenta':'Utilidad Retenida', 'monto': aportesSociales},
#         {'id':'resultadoDelEjercicio','cuenta':'Utilidad Retenida', 'monto': resultadoDelEjercicio},
#         {'id':'resultadoEjerciciosAnteriores','cuenta':'Utilidad Retenida', 'monto': resultadoEjerciciosAnteriores},
#         {'id':'totalPatrimonio','cuenta':'Utilidad Retenida', 'monto': totalPatrimonio},
#         {'id':'totalPasivoPatrimonio','cuenta':'Utilidad Retenida', 'monto': totalPasivoPatrimonio},
    ]    
    return balanceData

def detalleBalance(cuenta,fechaDesde, fechaHasta):
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

