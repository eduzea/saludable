from __future__ import division
from google.appengine.ext import ndb
from datetime import datetime, timedelta


class Record(ndb.Model):
    fechaCreacion = ndb.DateProperty()
    empleadoCreador = ndb.StringProperty(indexed=True)
    activo = ndb.BooleanProperty(default = True)

class Empleado(Record):
    nombre = ndb.StringProperty(indexed=True)
    apellido = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre + ' ' + self.apellido)
    email = ndb.StringProperty(indexed=True)
     
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
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.KeyProperty(kind=Ciudad)#donde esta el cliente
    sucursal = ndb.KeyProperty(kind=Sucursal, default=ndb.Key('Sucursal','Cali'))#que sucursal produce
    diasPago = ndb.IntegerProperty()
    grupoDePrecios = ndb.KeyProperty(kind=GrupoDePrecios)
    iva = ndb.BooleanProperty(default=True)
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

# def tryDiasPago(self):
#     try:
#         return self.cliente.get().diasPago
#     except Exception:
#         print 'Factura No. ', self.numero, ' Has client problem'
#         return 0

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

class InventarioRegistro(Record):
    fecha = ndb.DateProperty()
    sucursal = ndb.KeyProperty(kind=Sucursal)
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    existencias = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: '')

class Inventario(Record):
    sucursal = ndb.KeyProperty(kind=Sucursal)
    fecha = ndb.DateProperty()
    registros = ndb.KeyProperty(kind=InventarioRegistro, repeated = True)

class ExistenciasRegistro(InventarioRegistro):
    pass

class Existencias(Inventario):
    ultimoInventario = ndb.KeyProperty(kind=Inventario)
    ultimasFacturas = ndb.KeyProperty(kind=Factura, repeated=True)
    registros = ndb.KeyProperty(kind=ExistenciasRegistro, repeated = True)
    
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
    peso = ndb.IntegerProperty()
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
    pesoFruta = ndb.IntegerProperty()
    pesoPulpa = ndb.ComputedProperty(lambda self: pesoPulpa(self.productos))
    productos = ndb.StructuredProperty(ProductoPorcion, repeated=True)
    rendimiento = ndb.ComputedProperty(lambda self: 100 * self.pesoPulpa / self.pesoFruta)
    costoBruto = ndb.ComputedProperty(lambda self: self.pesoFruta * self.loteDeCompra.get().precio / self.pesoPulpa)


########## EGRESOS #######

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
    
# PUC classes - Consider implementing this from config...
class Clase(Record):
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    
class Grupo(Record):
    clase = ndb.KeyProperty(kind=Clase)
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Cuenta(Record):
    grupo = ndb.KeyProperty(kind=Grupo)
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class SubCuenta(Record):
    cuenta = ndb.KeyProperty(kind=Cuenta)
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

##################################################################################

class Bienoservicio(Record):
    nombre = ndb.StringProperty(indexed=True)
    tipo = ndb.KeyProperty(kind=TipoEgreso)
    clase = ndb.KeyProperty(kind=Clase)
    grupo = ndb.KeyProperty(kind=Grupo)
    cuenta = ndb.KeyProperty(kind=Cuenta)
    subcuenta = ndb.KeyProperty(kind=SubCuenta)
    puc = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    

class PorcionCompra(Record):
    valor = ndb.IntegerProperty()
    unidades = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: str(self.valor) + self.unidades)

class Compra(Record):
    bienoservicio = ndb.KeyProperty(kind=Bienoservicio)
    detalle = ndb.StringProperty()
    cantidad = ndb.IntegerProperty()
    precio = ndb.IntegerProperty()
    compra = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.bienoservicio.id())

class Fuente(Record):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Egreso(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    sucursal = ndb.KeyProperty(kind=Sucursal)
    fuente = ndb.KeyProperty(kind=Fuente, default=ndb.Key(Fuente,'CAJA.MENOR'))
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
    
class Deuda(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    empleado = ndb.KeyProperty(kind=Empleado)
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

class Pasivo(Record):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty() #Fecha de adquisicion
    empleado = ndb.KeyProperty(kind=Empleado)
    grupo = ndb.KeyProperty(kind=Grupo)
    cuenta = ndb.KeyProperty(kind=Cuenta)
    subcuenta = ndb.KeyProperty(kind=SubCuenta)
    total = ndb.IntegerProperty()
    
            