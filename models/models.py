from __future__ import division
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from datetime import datetime, timedelta
from google.appengine.ext.db import ComputedProperty
from protorpc import messages 

class Initialized(ndb.Model):
    pass

class Record(ndb.Model):
    fechaCreacion = ndb.DateProperty()
    empleadoCreador = ndb.StringProperty(indexed=True)
    activo = ndb.BooleanProperty(default = True)
    rotulo = ndb.ComputedProperty(lambda self: getRotulo(self))
    
def getRotulo(self):
    rotulo = '.'.join([key2str(getattr(self, key)) for key in keyDefs[self._class_name()]])
    return rotulo

def key2str(key):
    if type(key) is ndb.Key:
        return str(key.id())
    else:
        return str(key)

class Empleado(Record):
    nombre = ndb.StringProperty(indexed=True)
    apellido = ndb.StringProperty(indexed=True)
    writePermission = ndb.BooleanProperty()
    email = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre + ' ' + self.apellido)
     
class GrupoDePrecios(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Sucursal(Record):
    nombre = ndb.StringProperty()
    direccion = ndb.StringProperty()
    telefono = ndb.IntegerProperty()
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)
    
class Ciudad(Record):
    nombre = ndb.StringProperty()
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)
    
class Cliente(Record):
    nombre = ndb.StringProperty(indexed=True)
    negocio = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    contacto = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.KeyProperty(kind=Ciudad)#donde esta el cliente
    sucursal = ndb.KeyProperty(kind=Sucursal, default=ndb.Key('Sucursal','CALI'))#que sucursal produce
    diasPago = ndb.IntegerProperty()
    grupoDePrecios = ndb.KeyProperty(kind=GrupoDePrecios)
    iva = ndb.BooleanProperty(default=True)
    email = ndb.StringProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.nombre +' '+ self.negocio)
    
class Producto(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Porcion(Record):
    valor = ndb.IntegerProperty()
    unidades = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: str(self.valor) + self.unidades)

class Precio(Record):
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    grupoDePrecios = ndb.KeyProperty(kind=GrupoDePrecios)
    precio = ndb.IntegerProperty()
    
class Venta(Record):
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    cantidad = ndb.IntegerProperty()
    precio = ndb.IntegerProperty()
    venta = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.producto.id() +' '+ self.porcion.id())
    

class NumeroPedido(Record):
    consecutivo = ndb.IntegerProperty()

class NumeroFactura(Record):
    consecutivo = ndb.IntegerProperty()

class NumeroEgreso(Record):
    consecutivo = ndb.IntegerProperty()
    
class NumeroRemision(Record):
    consecutivo = ndb.IntegerProperty()

class NumeroDeuda(Record):
    consecutivo = ndb.IntegerProperty()
    
class NumeroOtrosIngresos(Record):
    consecutivo = ndb.IntegerProperty()
    
class NumeroActivoFijo(Record):
    consecutivo = ndb.IntegerProperty()

class NumeroPagoRecibido(Record):
    consecutivo = ndb.IntegerProperty()

class NumeroMovimientoDeEfectivo(Record):
    consecutivo = ndb.IntegerProperty()
    
class Remision(Record):
    numero = ndb.IntegerProperty()
    cliente = ndb.KeyProperty(kind=Cliente)
    empleado = ndb.KeyProperty(kind=Empleado)
    fecha = ndb.DateProperty()
    ventas = ndb.StructuredProperty(Venta,repeated=True)
    total = ndb.IntegerProperty()
    subtotal = ndb.IntegerProperty()
    iva = ndb.BooleanProperty(default=False)
    montoIva = ndb.FloatProperty(default=0.0)
    anulada = ndb.BooleanProperty(default=False)
    factura = ndb.IntegerProperty(default=0)

def fechaVencimientoCheck(factura):
    if factura.cliente.get():
        return datetime.combine(factura.fecha + timedelta(days = factura.cliente.get().diasPago),datetime.min.time())
    else:
        print 'WARNING: El cliente de la factura ', factura.numero, ' parece no existir'
        return datetime.today()

class Factura(Record):
    numero = ndb.IntegerProperty()
    cliente = ndb.KeyProperty(kind=Cliente)
    empleado = ndb.KeyProperty(kind=Empleado)
    fecha = ndb.DateProperty()
    ventas = ndb.StructuredProperty(Venta,repeated=True)
    total = ndb.IntegerProperty()    
    subtotal = ndb.IntegerProperty(default=0)
    iva = ndb.ComputedProperty(lambda self: True if self.montoIva else False)
    montoIva = ndb.IntegerProperty(default=0)
    anulada = ndb.BooleanProperty(default=False)
    #A hack to work around lack of support for datetime.date in computed properties...http://stackoverflow.com/questions/22652872/google-appengine-computed-property-date-return-throws-exception
    fechaVencimiento = ndb.ComputedProperty(lambda self: fechaVencimientoCheck(self) )
    pagada = ndb.BooleanProperty(default=False)
    #abono = ndb.IntegerProperty(repeated = True)
    pagoRef = ndb.IntegerProperty()
    remisiones = ndb.IntegerProperty(repeated = True)
    
class MedioDePago(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class CuentaTransferencias(Record):    
    numero = ndb.StringProperty(indexed=True)
    cliente = ndb.KeyProperty(kind=Cliente)
    rotulo = ndb.ComputedProperty(lambda self: self.cliente.id() + '-' + self.numero)
    
class PagoRecibido(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    oficina = ndb.StringProperty(indexed=True, default='')
    descripcion = ndb.StringProperty(indexed=True)
    comentario =  ndb.TextProperty()
    cliente = ndb.KeyProperty(kind=Cliente)
    medio = ndb.KeyProperty(kind=MedioDePago)
    documento = ndb.StringProperty(indexed=True)
    monto = ndb.IntegerProperty()
    facturas = ndb.IntegerProperty(repeated = True)
    
class Devolucion(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    factura = ndb.KeyProperty(kind=Factura)
    
class OtrosIngresos(Record):
    numero = ndb.IntegerProperty()
    empleado = ndb.KeyProperty(kind=Empleado)
    fecha = ndb.DateProperty()
    descripcion = ndb.TextProperty()
    total = ndb.IntegerProperty()
    
############ INVENTARIO ####################
class FraccionDeLote(Record):
    fecha = ndb.DateProperty()
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    cantidad = ndb.IntegerProperty()
    comentario = ndb.TextProperty()

# Uso esto porque el manejo de la StructuredProperties dificulta el 
# poner una referencia al padre en la clase misma, 
# por todo lo que se automatiza en el cliente a apartir de la definicion de la clase
# --> La verdadera solucion es escribir la logica para generar el HTML a partir de repeated key properties en
#     forma similar a como se hizo para Structured Propertties. 
class FraccionDeLoteUbicado(FraccionDeLote):
    ubicacion = ndb.StringProperty(indexed=True)

class Fila(Record):
    nombre=ndb.StringProperty(indexed=True)

class Columna(Record):
    nombre=ndb.IntegerProperty(indexed=True)
    
class Nivel(Record):
    nombre=ndb.IntegerProperty(indexed=True)

class UnidadDeAlmacenamiento(Record):
    fila = ndb.KeyProperty(kind = Fila)
    columna = ndb.KeyProperty(kind = Columna)
    nivel = ndb.KeyProperty(kind = Nivel)
    ubicacion = ndb.ComputedProperty(lambda self: '{0}.{1}.{2}'.format(self.fila.id(), self.columna.id(), self.nivel.id()))
    contenido = ndb.StructuredProperty(FraccionDeLote, repeated = True)

class TipoMovimiento(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    
class MovimientoDeInventario(Record):
    fecha = ndb.DateProperty()
    ubicacion = ndb.KeyProperty(kind = UnidadDeAlmacenamiento)
    tipo = ndb.KeyProperty(kind=TipoMovimiento)
    lote = ndb.KeyProperty(kind=FraccionDeLote, default = None)
    fechaLote = ndb.DateProperty()
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    cantidad = ndb.IntegerProperty()

class Pedido(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    fechaDeEntrega = ndb.DateProperty()
    cliente = ndb.KeyProperty(kind=Cliente)
    empleado = ndb.KeyProperty(kind=Empleado)
    items = ndb.StructuredProperty(Venta,repeated=True)
    factura = ndb.KeyProperty(kind=Factura, default = None)
    
class ProductoPorcion(Record):
    porcion = ndb.KeyProperty(kind=Porcion)
    cantidad = ndb.IntegerProperty()
    rotulo =  ndb.ComputedProperty(lambda self: self.porcion.id())

def pesoPulpa(productos):
    peso = 0
    for producto in productos:
        peso += producto.porcion.get().valor * producto.cantidad
    return peso / 1000

class Fruta(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Proveedor(Record):
    nombre = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.KeyProperty(kind=Ciudad)
    diasPago = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    bienesoservicios = ndb.KeyProperty(kind="Bienoservicio", repeated=True)
    textbienesoservicios =  ndb.ComputedProperty(lambda self: objListToString(self.bienesoservicios))


class LoteDeCompra(Record):
    fruta = ndb.KeyProperty(kind=Fruta)
    proveedor = ndb.KeyProperty(kind=Proveedor)
    fecha = ndb.DateProperty()
    precio = ndb.IntegerProperty()
    peso = ndb.FloatProperty()
    procesado = ndb.BooleanProperty(default = False)
    rotulo = ndb.ComputedProperty(lambda self: self.fruta.id() +'.'+ self.proveedor.id() + '.' + str(self.fecha))

def costoBruto(produccion):
    costo = produccion.pesoFruta * produccion.loteDeCompra.precio / produccion.pesoPulpa
    return costo

class Produccion(Record):
    fecha = ndb.DateProperty()
    sucursal = ndb.KeyProperty(kind=Sucursal)
    fruta = ndb.KeyProperty(kind=Fruta)
    loteDeCompra = ndb.KeyProperty(kind=LoteDeCompra)
    pesoFruta = ndb.FloatProperty()
    pesoPulpa = ndb.ComputedProperty(lambda self: pesoPulpa(self.productos))
    productos = ndb.StructuredProperty(ProductoPorcion, repeated=True)
    rendimiento = ndb.ComputedProperty(lambda self: 100 * self.pesoPulpa / self.pesoFruta)
    costoBruto = ndb.ComputedProperty(lambda self: self.pesoFruta * self.loteDeCompra.get().precio / self.pesoPulpa)


########## EGRESOS #######

#Deprecated. Replaced by the catefories of PUC itself.
class TipoEgreso(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

def objListToString(objList):
    text =''
    for obj in objList:
        if obj.get():
            text += obj.get().nombre + ';'
        else:
            print "Inconsistent record:", objList
    return text
    
# PUC classes - Initialize this once per datastore - Plan de Cuentas
class Clase(Record):
    pucnumber = ndb.StringProperty(indexed=True)
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    
class Grupo(Record):
    pucnumber = ndb.StringProperty(indexed=True)
    clase = ndb.KeyProperty(kind=Clase)
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Cuenta(Record):
    pucnumber = ndb.StringProperty(indexed=True)
    grupo = ndb.KeyProperty(kind=Grupo)
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class SubCuenta(Record):
    pucnumber = ndb.StringProperty(indexed=True)
    cuenta = ndb.KeyProperty(kind=Cuenta)
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

##################################################################################

### ------------BEGIN NUEVO MANEJO DE EGRESOS ----------####

class EstadoDePago(messages.Enum):
    Pagado = 0
    Pendiente = 1

class BienoservicioPUC(Record):
    nombre = ndb.StringProperty(indexed=True)
    pucNumero = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    
class Impuesto(Record):
    nombre = ndb.StringProperty(indexed=True)
    descripcion = ndb.TextProperty(indexed=True)
    cuentaPucNombre = ndb.StringProperty(indexed=True)
    cunetaPucNumero = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class CompraPUC(Record):
    bienoservicio = ndb.KeyProperty(kind=BienoservicioPUC)
    detalle = ndb.StringProperty()
    cantidad = ndb.FloatProperty()
    precio = ndb.IntegerProperty()
    monto = ndb.FloatProperty()
    impuestos = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.bienoservicio.id())
    
class FacturaDeProveedor(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    vencimiento = ndb.DateProperty()
    proveedor = ndb.KeyProperty(kind=Proveedor)
    compras = ndb.StructuredProperty(CompraPUC,repeated=True)
    baseImponible = ndb.IntegerProperty()
    impuesto = ndb.KeyProperty(kind=Impuesto)
    impuestoMonto = ndb.IntegerProperty()
    total = ndb.ComputedProperty(lambda self: self.baseImponible + self.impuestoMonto)
    estado = msgprop.EnumProperty(EstadoDePago, required=True, indexed=True) 

### ------------END NUEVO MANEJO DE EGRESOS ----------####

class Bienoservicio(Record):
    tipo = ndb.KeyProperty(kind=TipoEgreso)# Clasificacion economica (directo vs indirecto)
    clase = ndb.KeyProperty(kind=Clase)
    grupo = ndb.KeyProperty(kind=Grupo)
    cuenta = ndb.KeyProperty(kind=Cuenta, required=False)
    subcuenta = ndb.KeyProperty(kind=SubCuenta, required=False)
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)


class PorcionCompra(Record):
    valor = ndb.IntegerProperty()
    unidades = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: str(self.valor) + self.unidades)

class Compra(Record):
    egreso = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    proveedor = ndb.KeyProperty(kind=Proveedor)
    sucursal = ndb.KeyProperty(kind=Sucursal)
    bienoservicio = ndb.KeyProperty(kind=Bienoservicio)
    detalle = ndb.StringProperty()
    cantidad = ndb.FloatProperty()
    precio = ndb.IntegerProperty()
    compra = ndb.FloatProperty()# el valor total de la compra
    total = ndb.FloatProperty()# el valor total de la compra
    rotulo = ndb.ComputedProperty(lambda self: self.bienoservicio.id())
        
class Fuente(messages.Enum):
    Credito = 0
    Efectivo = 1

class Egreso(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    sucursal = ndb.KeyProperty(kind=Sucursal)
    fuente = msgprop.EnumProperty(Fuente, required=True, indexed=True, default=Fuente.Efectivo)
    empleado = ndb.KeyProperty(kind=Empleado)
    tipo = ndb.KeyProperty(kind=TipoEgreso)
    compras = ndb.StructuredProperty(Compra,repeated=True)
    proveedor = ndb.KeyProperty(kind=Proveedor)
    total = ndb.IntegerProperty()
    resumen = ndb.StringProperty(indexed=True)
    comentario = ndb.TextProperty()
   
    
class TipoAcreedor(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Acreedor(Record):
    tipo = ndb.KeyProperty(kind=TipoAcreedor)
    nombre = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)
    
class Pasivo(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    grupo = ndb.KeyProperty(kind=Grupo)
    cuenta = ndb.KeyProperty(kind=Cuenta)
    acreedor = ndb.KeyProperty(kind=Acreedor)
    monto = ndb.IntegerProperty()
    interes = ndb.FloatProperty(default=0)
    vencimiento = ndb.DateProperty()
    comentario = ndb.TextProperty()
    montoPagado = ndb.IntegerProperty(default=0)
    pagada = ndb.ComputedProperty(lambda self: 100 * self.montoPagado / self.monto)

class CapitalPagado(Record):
    fecha = ndb.DateProperty()
    valor = ndb.IntegerProperty()

class CapitalSocial(Record):
    socio = ndb.StringProperty(indexed=True)
    acciones = ndb.IntegerProperty()
    total =  ndb.IntegerProperty()
    participacion = ndb.ComputedProperty(lambda self: 100 * self.total / CapitalPagado.query().fetch()[-1].valor)
    rotulo= ndb.ComputedProperty(lambda self: self.socio)
    
class Activo(Record):
    numero = ndb.IntegerProperty()
    nombre = ndb.StringProperty(indexed=True)
    grupo = ndb.KeyProperty(kind=Grupo)
    cuenta = ndb.KeyProperty(kind=Cuenta)
    subcuenta = ndb.KeyProperty(kind=SubCuenta)
    comentario = ndb.TextProperty()

class ActivoFijo(Activo):
    fechaDeAdquisicion = ndb.DateProperty() #Fecha de adquisicion del activo
    precioUnitario = ndb.IntegerProperty()
    cantidad = ndb.IntegerProperty()
    valorPagado = ndb.ComputedProperty(lambda self: self.precioUnitario * self.cantidad)
    valorActual = ndb.IntegerProperty()#depreciacion aqui
    total = ndb.ComputedProperty(lambda self: self.valorActual)
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)

class Banco(Record):
    nombre = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    contacto = ndb.StringProperty(indexed=True)
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)

class TipoDeCuenta(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)    

class CuentaBancaria(Record):
    numero = ndb.StringProperty(indexed=True)
    banco = ndb.KeyProperty(kind=Banco)
    tipo = ndb.KeyProperty(kind=TipoDeCuenta)
    titular = ndb.StringProperty(indexed=True)
    rotulo= ndb.ComputedProperty(lambda self: self.banco.get().rotulo +'-' + self.numero)

class TipoMovimientoEfectivo(messages.Enum):
    Credito = 0
    Debito = 1

class MovimientoDeEfectivo(Record):
    numero = ndb.IntegerProperty()
    cuenta = ndb.KeyProperty(kind=CuentaBancaria)
    fecha = ndb.DateProperty()
    tipoMovimiento = msgprop.EnumProperty(TipoMovimientoEfectivo, required=True, indexed=True)
    descripcion = ndb.StringProperty()
    info = ndb.StringProperty()
    monto = ndb.IntegerProperty()
    saldo = ndb.IntegerProperty()
    egresos = ndb.KeyProperty(kind=Egreso, repeated=True)
    reconciliado = ndb.BooleanProperty()     

class SaldoCuentaBancaria(Record):
    cuenta = ndb.KeyProperty(kind=CuentaBancaria)
    fecha = ndb.DateProperty()
    saldo = ndb.IntegerProperty()

class CuentaPorCobrar(Record):
    deudor = ndb.KeyProperty(kind=Cliente)
    facturas = ndb.KeyProperty(kind=Factura, repeated=True)
    total = ndb.ComputedProperty(lambda self: sum([factura.get().total for factura in self.facturas]))

class AnticipoImpuestos(Activo):
    entidad = ndb.StringProperty(indexed=True)
    total = ndb.IntegerProperty()
    
keyDefs = {'Cliente':['nombre','negocio'],
           'Producto':['nombre'], 
           'Porcion':['valor','unidades'], 
           'GrupoDePrecios':['nombre'],
           'Precio':['producto','porcion','grupoDePrecios'], 
           'Empleado':['nombre','apellido'],
           'Sucursal':['nombre'],
           'Ciudad':['nombre'],
           'Pedido':['numero'], 
           'Factura':['numero'],
           'Venta':['producto','porcion'],
           'Egreso':['numero'],
           'LoteDeCompra':['fecha','fruta','proveedor'],
           'Compra':['egreso','bienoservicio','detalle'], 
           'Remision':['numero'],
           'Proveedor':['nombre'],
           'Bienoservicio':['nombre'],
           'Fruta':['nombre'],
           'LoteDeCompra':['fruta','proveedor','fecha'],
           'PorcionCompra':['valor','unidades'],
           'TipoEgreso':['nombre'],
           'TipoAcreedor':['nombre'],
           'Acreedor':['nombre'],
           'Pasivo':['numero'],
           'Clase':['pucnumber'],
           'Grupo':['pucnumber'],
           'Cuenta':['pucnumber'],
           'SubCuenta':['pucnumber'],
           'OtrosIngresos':['numero'],
           'CapitalSocial':['socio'],
           'CapitalPagado':['fecha'],
           'ActivoFijo':['numero'],
           'CuentaBancaria':['numero'],
           'Banco':['nombre'],
           'TipoDeCuenta':['nombre'],
           'SaldoCuentaBancaria':['fecha','cuenta'],
           'CuentaPorCobrar':['cliente'],
           'MedioDePago':['nombre'],
           'CuentaTransferencias':['numero'],
           'PagoRecibido':['numero'],
           'TipoMovimiento':['nombre'],
           'Existencias':['fecha','producto','porcion'],
           'MovimientoDeInventario':['fecha','ubicacion','tipo','fechaLote','producto','porcion'],
           'UnidadDeAlmacenamiento':['fila','columna','nivel'],
           'FraccionDeLote':['fecha','producto','porcion'],
           'FraccionDeLoteUbicado':['ubicacion','fecha','producto','porcion'],
           'ExistenciasRegistro':['sucursal','producto','porcion'],
           'Produccion':['fecha','sucursal','fruta'],
           'ProductoPorcion':['porcion'],
           'Fuente':['nombre'],
           'Fila':['nombre'],
           'Columna':['nombre'],
           'Nivel':['nombre'],
           'MovimientoDeEfectivo':['numero'],
           ##########
           'NumeroPedido':['consecutivo'],
           'NumeroFactura':['consecutivo'],
           'NumeroRemision':['consecutivo'],
           'NumeroEgreso':['consecutivo'],              
           'NumeroDeuda':['consecutivo'],
           'NumeroOtrosIngresos':['consecutivo'],
           'NumeroActivoFijo':['consecutivo'],
           'NumeroPagoRecibido':['consecutivo'],
           'NumeroMovimientoDeEfectivo':['consecutivo'],
           }
classModels = {'Cliente':Cliente, 
               'Producto':Producto,
               'Porcion':Porcion, 
               'Precio':Precio, 
               'GrupoDePrecios':GrupoDePrecios,
               'Pedido':Pedido,
               'Factura':Factura, 
               'Remision':Remision ,
               'Empleado':Empleado, 
               'NumeroFactura':NumeroFactura, 
               'NumeroPedido':NumeroPedido, 
               'Venta':Venta,
               'Proveedor':Proveedor, 
               'Bienoservicio':Bienoservicio,
               'Fruta':Fruta,
               'LoteDeCompra':LoteDeCompra,
               'LoteDeCompra':LoteDeCompra,
               'Clase':Clase,
               'Grupo':Grupo,
               'Cuenta':Cuenta,
               'SubCuenta':SubCuenta, 
               'PorcionCompra':PorcionCompra, 
               'Egreso':Egreso,
               'Fuente':Fuente,
               'Compra':Compra,
               'TipoEgreso':TipoEgreso,
               'TipoAcreedor':TipoAcreedor,
               'Sucursal':Sucursal,
               'Ciudad':Ciudad,
               'Acreedor':Acreedor,
               'Pasivo':Pasivo,
               'Devolucion':Devolucion,
               'OtrosIngresos':OtrosIngresos,
               'CapitalSocial':CapitalSocial,
               'CapitalPagado':CapitalPagado,
               'ActivoFijo':ActivoFijo,
               'CuentaBancaria':CuentaBancaria,
               'Banco':Banco,
               'TipoDeCuenta':TipoDeCuenta,
               'SaldoCuentaBancaria':SaldoCuentaBancaria,
               'CuentaPorCobrar':CuentaPorCobrar,
               'MedioDePago':MedioDePago,
               'CuentaTransferencias':CuentaTransferencias,
               'PagoRecibido':PagoRecibido,
               'FraccionDeLote':FraccionDeLote,
               'FraccionDeLoteUbicado':FraccionDeLoteUbicado,               
               'MovimientoDeInventario':MovimientoDeInventario,
               'TipoMovimiento':TipoMovimiento,
               'UnidadDeAlmacenamiento':UnidadDeAlmacenamiento,
               'Fila':Fila,
               'Columna':Columna,
               'Nivel':Nivel,
               'Produccion':Produccion,
               'ProductoPorcion':ProductoPorcion,
               'Fuente':Fuente,
               'EstadoDePago':EstadoDePago,
               'FacturaDeProveedor':FacturaDeProveedor,
               'MovimientoDeEfectivo':MovimientoDeEfectivo}

singletons = {'NumeroPedido': NumeroPedido,
              'NumeroFactura':NumeroFactura,
              'NumeroRemision':NumeroRemision,
              'NumeroEgreso':NumeroEgreso,              
              'NumeroDeuda':NumeroDeuda,
              'NumeroOtrosIngresos':NumeroOtrosIngresos,
              'NumeroActivoFijo':NumeroActivoFijo,
              'NumeroPagoRecibido':NumeroPagoRecibido,
              'NumeroMovimientoDeEfectivo':NumeroMovimientoDeEfectivo
              }
