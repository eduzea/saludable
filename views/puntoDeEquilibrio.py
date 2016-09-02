'''
Created on Aug 29, 2016

@author: eduze_000
'''
from easydict import EasyDict as edict
from datastorelogic import DataStoreInterface
import calendar
from datetime import date

############# Init the instance! ################# There's probably a better way!
if 'dataStoreInterface' not in globals():
    dataStoreInterface = DataStoreInterface()

##################### FORMULAS PUNTO DE EQUILIBRIO ##################################

# This function assumes the queried entities have a 'total' field
def getTotalFromModel(model, qryParams):
    query = dataStoreInterface.buildQuery(model, qryParams)
    entities = query.fetch()
    return edict({'total': sum([entity.total for entity in entities]), 'data':entities })

def getVentasNetas(fechaDesde, fechaHasta):
    ventasPyG = getTotalFromModel('Factura', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta}).total
    devoluciones = getTotalFromModel('Devolucion', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta}).total
    return ventasPyG - devoluciones

costosDeProduccionFijos = [  'ARRIENDO',
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
    
gastosDeAdminVentasFijos = [ 'NOMINA.-.ADMINISTRATIVA',
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
costosDeProduccionVariables = [  'MATERIA.PRIMA-FRUTA',
                            'MATERIA.PRIMA-BOLSAS.PLASTICAS',
                            'MATERIA.PRIMA-VARIOS',
                            'MATERIA.PRIMA-QUIMICOS',
                            'PLASTICOS',
                            'MATERIA.PRIMA-HIELO.SECO'
                            ]
    
gastosDeAdminVentasVariables = ['TRANSPORTE.DEL.PRODUCTO-INTERMUNICIPAL',
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

def getCostosFijos(fechaDesde, fechaHasta):


    
    costos = getTotalFromModel('Egreso', {'resumen':costosDeProduccionFijos,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta}).total
    gastos = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentasFijos,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta}).total
    return costos + gastos

def getCostosVariables(fechaDesde, fechaHasta):
    
    costos = getTotalFromModel('Egreso', {'resumen':costosDeProduccionVariables,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta}).total
    gastos = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentasVariables,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta}).total
    return costos + gastos

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

def getUtilidadDataFull(fechaDesde, fechaHasta):
    registros = []
    ventas = getTotalFromModel('Factura', {'fechaDesde':fechaDesde, 'fechaHasta': fechaHasta})
    costosVariables = getTotalFromModel('Egreso', {'resumen':costosDeProduccionVariables,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    gastosVariables = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentasVariables,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    costosFijos = getTotalFromModel('Egreso', {'resumen':costosDeProduccionFijos,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta})
    gastosFijos = getTotalFromModel('Egreso', {'resumen':gastosDeAdminVentasFijos,
                                                 'fechaDesde':fechaDesde,
                                                 'fechaHasta': fechaHasta}) 
    
    monthData = {'Ventas':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
                 'Costos Variables':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
                 'Gastos Variables':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
                 'Costos Fijos':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0},
                 'Gastos Fijos':{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0} }
    
    for factura in ventas.data:
        registros.append({'tipo':'Ventas', 'sortRows':1 ,'detalle':factura.cliente.id(),'mesnum':factura.fecha.month,'mes': calendar.month_abbr[factura.fecha.month],'total':factura.total})
        monthData['Ventas'][factura.fecha.month] += factura.total
    
    for egreso in costosVariables.data:
        registros.append({'tipo':'Costos Variables', 'sortRows':2 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month],'total':egreso.total})
        monthData['Costos Variables'][egreso.fecha.month] += egreso.total
        
    for egreso in gastosVariables.data:
        registros.append({'tipo':'Gastos Variables', 'sortRows':3 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month],'total':egreso.total})
        monthData['Gastos Variables'][egreso.fecha.month] += egreso.total
        
    for egreso in costosFijos.data:
        registros.append({'tipo':'Costos Fijos', 'sortRows':6 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month], 'total':egreso.total})
        monthData['Costos Fijos'][egreso.fecha.month] += egreso.total
     
    for egreso in gastosFijos.data:
        registros.append({'tipo':'Gastos Fijos', 'sortRows':7 ,'detalle':egreso.resumen,'mesnum':egreso.fecha.month, 'mes': calendar.month_abbr[egreso.fecha.month], 'total':egreso.total})    
        monthData['Gastos Fijos'][egreso.fecha.month] += egreso.total
    
    utilidadBruta=[]
    margenBruto = []
    utilidadNeta =[]
    margenNeto = []
    maxMonth = date.today().month
    for month in range(1, maxMonth+1):
        try:
            utilidadBruta.append(monthData['Ventas'][month] - monthData['Costos Variables'][month] - monthData['Gastos Variables'][month])
            utilidadNeta.append(utilidadBruta[month-1] - monthData['Costos Fijos'][month] - monthData['Gastos Fijos'][month])
            margenBruto.append(100.0 * utilidadBruta[month-1] / monthData['Ventas'][month])
            margenNeto.append(100.0 * utilidadNeta[month-1] / monthData['Ventas'][month])
            registros.append({'tipo':'Utilidad Bruta','sortRows':4,'detalle':'Utilidad Bruta','mesnum':month,'mes': calendar.month_abbr[month],'total': utilidadBruta[month-1]})
            registros.append({'tipo':'Margen Bruto(%)','sortRows':5,'detalle':'Margen Bruto','mesnum':month,'mes': calendar.month_abbr[month],'total':margenBruto[month-1]})
            registros.append({'tipo':'Utilidad Neta','sortRows':8,'detalle':'Utilidad Neta','mesnum':month,'mes': calendar.month_abbr[month],'total':utilidadNeta[month-1]})
            registros.append({'tipo':'Margen Neto(%)','sortRows':9,'detalle':'Margen Neto','mesnum':month,'mes': calendar.month_abbr[month],'total':margenNeto[month-1]})
        except:
            print month, ", ", maxMonth
    return registros

