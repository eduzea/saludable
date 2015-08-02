from google.appengine.ext import ndb


class Empleado(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    apellido = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre + ' ' + self.apellido)
    email = ndb.StringProperty(indexed=True)
    activo = ndb.BooleanProperty(default=True)

class Record(ndb.Model):
    fechaCreacion = ndb.DateProperty()
    empleadoCreador = ndb.StringProperty(indexed=True)
     

class GrupoDePrecios(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Sucursal(ndb.Model):
    nombre = ndb.StringProperty()
    direccion = ndb.StringProperty()
    telefono = ndb.IntegerProperty()
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)
    
class Ciudad(ndb.Model):
    nombre = ndb.StringProperty()
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)
    
class Cliente(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    negocio = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.KeyProperty(kind=Ciudad)
    diasPago = ndb.IntegerProperty()
    grupoDePrecios = ndb.KeyProperty(kind=GrupoDePrecios)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre +' '+ self.negocio)
    
class Producto(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Porcion(ndb.Model):
    valor = ndb.IntegerProperty()
    unidades = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: str(self.valor) + self.unidades)

class Precio(ndb.Model):
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    grupoDePrecios = ndb.KeyProperty(kind=GrupoDePrecios)
    precio = ndb.IntegerProperty()
    
class Venta(ndb.Model):
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    cantidad = ndb.IntegerProperty()
    precio = ndb.IntegerProperty()
    venta = ndb.IntegerProperty()

class NumeroFactura(ndb.Model):
    consecutivo = ndb.IntegerProperty()

class NumeroEgreso(ndb.Model):
    consecutivo = ndb.IntegerProperty()
    
class NumeroRemision(ndb.Model):
    consecutivo = ndb.IntegerProperty()

class NumeroDeuda(ndb.Model):
    consecutivo = ndb.IntegerProperty()
    
class NumeroOtrosIngresos(ndb.Model):
    consecutivo = ndb.IntegerProperty()
    
class NumeroActivoFijo(ndb.Model):
    consecutivo = ndb.IntegerProperty()

class NumeroPagoRecibido(ndb.Model):
    consecutivo = ndb.IntegerProperty()
    
class Remision(ndb.Model):
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
    
class Factura(ndb.Model):
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
    pagada = ndb.BooleanProperty(default=False)
    abono = ndb.IntegerProperty(repeated = True)
    pagoRef = ndb.IntegerProperty(repeated = True)
#     resumen = ndb.ComputedProperty(lambda self: self.ventas[0].producto.id())#consider a better option for this!
    
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
    cliente = ndb.KeyProperty(kind=Cliente)
    medio = ndb.KeyProperty(kind=MedioDePago)
    documento = ndb.StringProperty(indexed=True)
    monto = ndb.IntegerProperty()
    
class Devolucion(ndb.Model):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    factura = ndb.KeyProperty(kind=Factura)
    
class OtrosIngresos(ndb.Model):
    numero = ndb.IntegerProperty()
    empleado = ndb.KeyProperty(kind=Empleado)
    fecha = ndb.DateProperty()
    descripcion = ndb.TextProperty()
    total = ndb.IntegerProperty()
    
############ INVENTARIO ####################

class InventarioRegistro(Record):
    fecha = ndb.DateProperty()
    ciudad = ndb.KeyProperty(kind=Ciudad)
    producto = ndb.KeyProperty(kind=Producto)
    porcion = ndb.KeyProperty(kind=Porcion)
    existencias = ndb.IntegerProperty()

class Inventario(Record):
    ciudad = ndb.KeyProperty(kind=Ciudad)
    fecha = ndb.DateProperty()
    registros = ndb.KeyProperty(kind=InventarioRegistro, repeated = True)

class Existencias(Inventario):
    ultimoInventario = ndb.KeyProperty(kind=Inventario)
    ultimasFacturas = ndb.KeyProperty(kind=Factura, repeated=True)
    


########## EGRESOS #######

class TipoEgreso(ndb.Model):
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
    

class Proveedor(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
    diasPago = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    bienesoservicios = ndb.KeyProperty(kind="Bienoservicio", repeated=True)
    textbienesoservicios =  ndb.ComputedProperty(lambda self: objListToString(self.bienesoservicios))

# PUC classes - Consider implementing this from config...
class Clase(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    
class Grupo(ndb.Model):
    clase = ndb.KeyProperty(kind=Clase)
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Cuenta(ndb.Model):
    grupo = ndb.KeyProperty(kind=Grupo)
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class SubCuenta(ndb.Model):
    cuenta = ndb.KeyProperty(kind=Cuenta)
    nombre = ndb.StringProperty(indexed=True)
    pucNumber = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

##################################################################################

class Bienoservicio(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    tipo = ndb.KeyProperty(kind=TipoEgreso)
    clase = ndb.KeyProperty(kind=Clase)
    grupo = ndb.KeyProperty(kind=Grupo)
    cuenta = ndb.KeyProperty(kind=Cuenta)
    subcuenta = ndb.KeyProperty(kind=SubCuenta)
    puc = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class PorcionCompra(ndb.Model):
    valor = ndb.IntegerProperty()
    unidades = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: str(self.valor) + self.unidades)

class Compra(ndb.Model):
    bienoservicio = ndb.KeyProperty(kind=Bienoservicio)
    detalle = ndb.StringProperty()
    cantidad = ndb.IntegerProperty()
    precio = ndb.IntegerProperty()
    compra = ndb.IntegerProperty()

class Egreso(ndb.Model):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    sucursal = ndb.KeyProperty(kind=Sucursal)
    empleado = ndb.KeyProperty(kind=Empleado)
    tipo = ndb.KeyProperty(kind=TipoEgreso)
    compras = ndb.StructuredProperty(Compra,repeated=True)
    proveedor = ndb.KeyProperty(kind=Proveedor)
    total = ndb.IntegerProperty()
    resumen = ndb.StringProperty(indexed=True)
    comentario = ndb.TextProperty()
    
class TipoAcreedor(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Acreedor(ndb.Model):
    tipo = ndb.KeyProperty(kind=TipoAcreedor)
    nombre = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)
    
class Deuda(ndb.Model):
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
    valorPagado = ndb.IntegerProperty()
    valorActual = ndb.IntegerProperty()
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
    
            