'''
Created on Aug 8, 2015

@author: eduze_000
'''
from easydict import EasyDict as edict
from datastorelogic import buildQuery

##################### FORMULAS P&G ##################################
# This function assumes the queried entities have a 'total' field
def getTotalFromModel(model, qryParams):
#     qryParams.pop("resumen", None)
    query = buildQuery(model, qryParams)
    entities = query.fetch()
    if entities:
        return sum([entity.total for entity in entities])
    else:
        return 0

def getDepreciaciones(fechaDesde, fechaHasta):
    return 0 # Figure out what this should be

def getServiciosPublicos(fechaDesde, fechaHasta):
    electricidad = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Energia',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    telecom = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Telecomunicaciones',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    gas = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Gas',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    agua = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Agua',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    return edict({'total': electricidad + telecom + gas + agua,
                  'electricidad':electricidad,'telecom':telecom,'gas':gas,'agua':agua})


def getCostosIndirectos(fechaDesde, fechaHasta):
    serviciosPublicos = getServiciosPublicos(fechaDesde, fechaHasta)
    arriendo = getTotalFromModel('Egreso', {'resumen':'Arriendo',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta}
                                 )
    varios = getTotalFromModel('Egreso', {'resumen':['Servicios-Varios',
                                                     'Servicios-Fumigacion',
                                                     'Alimentacion.Empleado',
                                                     'Utensilios',
                                                     'Vigilancia',
                                                     'Combustible',
                                                     'Dotacion',
                                                     'Dotacion.empleados',
                                                     'Pruebas.laboratorio',
                                                     'Cursos.para.el.personal',
                                                     'Medicinas.Botiquin'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta}
                               )
    return edict({'total':serviciosPublicos.total + arriendo + varios,
            'serviciosPublicos':serviciosPublicos,'arriendo':arriendo,'varios':varios})

def getManoDeObra(fechaDesde, fechaHasta):
    manoDeObraDirecta = getTotalFromModel('Egreso', {'resumen':'Nomina.-.Operativa',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    manoDeObraIndirecta = getTotalFromModel('Egreso', {'resumen':'Nomina-Turnos',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    return edict({'total' : manoDeObraDirecta + manoDeObraIndirecta,
            'manoDeObraDirecta': manoDeObraDirecta, 'manoDeObraIndirecta': manoDeObraIndirecta})

def getMateriaPrima(fechaDesde, fechaHasta):
    materiaPrimaFruta = getTotalFromModel('Egreso', {'resumen':'Materia.Prima-Fruta',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    materiaPrimaVarios = getTotalFromModel('Egreso', {'resumen':['Materia.Prima-Bolsas.Plasticas',
                                                                 'Materia.Prima-Varios',
                                                                 'Materia.Prima-Quimicos',
                                                                 'Materia.Prima-Implementos.de.Aseo',
                                                                 'Materia.Prima-Hielo.Seco',
                                                                 ],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    return edict({'total':materiaPrimaFruta + materiaPrimaVarios,
            'materiaPrimaFruta':materiaPrimaFruta, 'materiaPrimaVarios':materiaPrimaVarios}) 

def getCostosDeProduccion(fechaDesde, fechaHasta):
    materiaPrima = getMateriaPrima(fechaDesde, fechaHasta)
    manoDeObra = getManoDeObra(fechaDesde, fechaHasta)
    costosIndirectos = getCostosIndirectos(fechaDesde, fechaHasta)
    depreciaciones = getDepreciaciones(fechaDesde, fechaHasta)
    return edict({'total': materiaPrima.total + manoDeObra.total + costosIndirectos.total + depreciaciones,
            'materiaPrima':materiaPrima , 'manoDeObra':manoDeObra , 'costosIndirectos':costosIndirectos , 'depreciaciones':depreciaciones})
    
def getVentasNetas(fechaDesde, fechaHasta):
    ventasPyG = getTotalFromModel('Factura', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta})
    devoluciones = getTotalFromModel('Devolucion', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta})
    return edict({'total': ventasPyG - devoluciones, 'ventas': ventasPyG, 'devoluciones': devoluciones})

def getGastosDeVentas(fechaDesde,fechaHasta):
    impuestos = getTotalFromModel('Egreso', {'resumen':['Impuesto.de.Industria.y.Comercio'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    transportes = getTotalFromModel('Egreso', {'resumen':['Transporte.del.Producto-Local',
                                                        'Transporte.del.Producto-Intermunicipal',
                                                        'Taxis.y.Pasajes.de.Bus'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    mantenimientoVehiculos = getTotalFromModel('Egreso', {'resumen':'Mantenimiento.de.vehiculos',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    parqueadero = getTotalFromModel('Egreso', {'resumen':'Parqueadero',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    publicidad = getTotalFromModel('Egreso', {'resumen':'Publicidad',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    return edict({'total': impuestos + transportes + mantenimientoVehiculos + parqueadero + publicidad,
            'impuestos':impuestos,'transportes':transportes,'mantenimientoVehiculos':mantenimientoVehiculos,
            'parqueadero':parqueadero,'publicidad':publicidad})

def getGastosAdministrativos(fechaDesde,fechaHasta):
    gastosDePersonal = getTotalFromModel('Egreso', {'resumen':['Nomina.-.Administrativa',
                                                               'Aportes.Pension'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    honorarios = getTotalFromModel('Egreso', {'resumen':'Honorarios',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    mantenimientoYreparaciones = getTotalFromModel('Egreso', {'resumen':['Mantenimiento.y.arreglos.locativos',
                                                                         'Materiales.de.Construccion'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    gastosLegales = getTotalFromModel('Egreso', {'resumen':'Gastos.legales',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    papeleriaYfotocopias =  getTotalFromModel('Egreso', {'resumen':'Papeleria',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    camaraDeComercio = getTotalFromModel('Egreso', {'resumen':'Camara.de.comercio',
                                                    'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    return edict({'total': gastosDePersonal + honorarios + mantenimientoYreparaciones + gastosLegales + papeleriaYfotocopias + camaraDeComercio,
            'gastosDePersonal':gastosDePersonal,'honorarios':honorarios, 'mantenimientoYreparaciones':mantenimientoYreparaciones,
            'gastosLegales' : gastosLegales, 'papeleriaYfotocopias': papeleriaYfotocopias, 'camaraDeComercio': camaraDeComercio})

def getOtrosGastos(fechaDesde, fechaHasta):
    gastosFinancieros = getTotalFromModel('Egreso', {'resumen':'Servicios.Financieros',
                                                    'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    gastosExtraordinarios = getTotalFromModel('Egreso', {'resumen':'Gastos.Extraordinarios',
                                                    'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    return edict({'total': gastosFinancieros + gastosExtraordinarios,
            'financieros':gastosFinancieros,'extraordinarios':gastosExtraordinarios})

def getIngresosNoOperacionales(fechaDesde, fechaHasta):
    return getTotalFromModel('OtrosIngresos', {'fechaDesde':fechaDesde, 'fechaHasta': fechaHasta})

def getImpuestos(fechaDesde, fechaHasta):
    renta = getTotalFromModel('Egreso', {'resumen':['Impuesto.-.Renta'], 
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta':fechaHasta})
    cree = getTotalFromModel('Egreso', {'resumen':'Impuesto.-.CREE', 
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta':fechaHasta})
    return edict({'total':renta + cree, 'renta':renta, 'cree':cree})

def getPyGData(fechaDesde,fechaHasta):
    ventasNetas = getVentasNetas(fechaDesde, fechaHasta)
    costos = getCostosDeProduccion(fechaDesde, fechaHasta)
    utilidadBruta = ventasNetas.total - costos.total
    margenBruto = utilidadBruta/ventasNetas.total
    gastosDeVentas = getGastosDeVentas(fechaDesde,fechaHasta)
    gastosAdministrativos = getGastosAdministrativos(fechaDesde,fechaHasta)
    utilidadOperacional = ventasNetas.total - costos.total - gastosAdministrativos.total - gastosDeVentas.total
    margenOperacional = utilidadOperacional / ventasNetas.total
    otrosGastos = getOtrosGastos(fechaDesde, fechaHasta)
    ingresosNoOperacionales = getIngresosNoOperacionales(fechaDesde, fechaHasta)
    utilidadAntesDeImpuestos = utilidadOperacional - otrosGastos.total + ingresosNoOperacionales
    margenAntesDeImpuestos = utilidadAntesDeImpuestos / ventasNetas.total
    impuestos = getImpuestos(fechaDesde,fechaHasta)
    utilidadNeta = utilidadAntesDeImpuestos - impuestos.total 
    margenNeto = utilidadNeta/ventasNetas.total
    return {'desde':fechaDesde,
            'hasta':fechaHasta,
            'ventasNetas': '${:,}'.format(ventasNetas.total) , 
            'ventas': '${:,}'.format(ventasNetas.ventas),
            'devoluciones':'${:,}'.format(ventasNetas.devoluciones), 
            'costos': '${:,}'.format(costos.total),
            'materiaPrima':'${:,}'.format(costos.materiaPrima.total),
            'materiaPrimaFruta':'${:,}'.format(costos.materiaPrima.materiaPrimaFruta),
            'materiaPrimaVarios':'${:,}'.format(costos.materiaPrima.materiaPrimaVarios),
            'manoDeObra':'${:,}'.format(costos.manoDeObra.total),
            'manoDeObraDirecta':'${:,}'.format(costos.manoDeObra.manoDeObraDirecta),
            'manoDeObraIndirecta':'${:,}'.format(costos.manoDeObra.manoDeObraIndirecta),
            'costosIndirectos':'${:,}'.format(costos.costosIndirectos.total),
            'serviciosPublicos': '${:,}'.format(costos.costosIndirectos.serviciosPublicos.total),
            'electricidad':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.electricidad),
            'gas':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.gas),
            'telecom':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.telecom),
            'agua':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.agua),
            'arriendo' : '${:,}'.format(costos.costosIndirectos.arriendo),
            'costosIndirectosVarios': '${:,}'.format(costos.costosIndirectos.varios),
            'depreciaciones': '${:,}'.format(getDepreciaciones(fechaDesde, fechaHasta)), 
            'utilidadBruta' : '${:,}'.format(utilidadBruta),
            'margenBruto': '{:.2%}'.format(margenBruto),
            'gastosDeVentas':'${:,}'.format(gastosDeVentas.total),
            'gastosDeVentasImpuestos':'${:,}'.format(gastosDeVentas.impuestos),
            'transportes':'${:,}'.format(gastosDeVentas.transportes),
            'mantenimientoVehiculos':'${:,}'.format(gastosDeVentas.mantenimientoVehiculos),
            'parqueadero':'${:,}'.format(gastosDeVentas.parqueadero),
            'publicidad':'${:,}'.format(gastosDeVentas.publicidad),
            'gastosAdministrativos':'${:,}'.format(gastosAdministrativos.total),
            'gastosDePersonal':'${:,}'.format(gastosAdministrativos.gastosDePersonal),
            'honorarios':'${:,}'.format(gastosAdministrativos.honorarios),
            'mantenimientoYreparaciones':'${:,}'.format(gastosAdministrativos.mantenimientoYreparaciones),
            'gastosLegales':'${:,}'.format(gastosAdministrativos.gastosLegales),
            'papeleriaYfotocopias':'${:,}'.format(gastosAdministrativos.papeleriaYfotocopias),
            'camaraDeComercio':'${:,}'.format(gastosAdministrativos.camaraDeComercio),
            'utilidadOperacional':'${:,}'.format(utilidadOperacional),
            'margenOperacional':'{:.2%}'.format(margenOperacional),
            'ingresosNoOperacionales':'${:,}'.format(ingresosNoOperacionales),
            'otrosGastos':'${:,}'.format(otrosGastos.total),
            'financieros':'${:,}'.format(otrosGastos.financieros),
            'extraordinarios':'${:,}'.format(otrosGastos.extraordinarios),
            'utilidadAntesDeImpuestos':'${:,}'.format(utilidadAntesDeImpuestos),
            'margenAntesDeImpuestos':'{:.2%}'.format(margenAntesDeImpuestos),
            'impuestos':'${:,}'.format(impuestos.total),
            'renta':'${:,}'.format(impuestos.renta),
            'cree':'${:,}'.format(impuestos.cree),
            'utilidadNeta':'${:,}'.format(utilidadNeta),
            'margenNeto': '{:.2%}'.format(margenNeto)
    }