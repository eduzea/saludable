from google.appengine.ext import ndb

class Empleado(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    apellido = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre + ' ' + self.apellido)

class GrupoDePrecios(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Cliente(ndb.Model):
    """Models an individual Client."""
    nombre = ndb.StringProperty(indexed=True)
    negocio = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
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
    grupo = ndb.KeyProperty(kind=GrupoDePrecios)
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
    subtotal = ndb.IntegerProperty(default=0.0)
    iva = ndb.BooleanProperty(default=False)
    montoIva = ndb.FloatProperty(default=0.0)
    anulada = ndb.BooleanProperty(default=False)

########## EGRESOS #######

class TipoEgreso(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

def objListToString(objList):
    text =''
    for obj in objList:
        text += obj.get().nombre + ';'
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

class Bienoservicio(ndb.Model):
    tipo = ndb.KeyProperty(kind=TipoEgreso)
    nombre = ndb.StringProperty(indexed=True)
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

class Sucursal(ndb.Model):
    nombre = ndb.StringProperty()
    direccion = ndb.StringProperty()
    telefono = ndb.IntegerProperty()
    rotulo= ndb.ComputedProperty(lambda self: self.nombre)

class Egreso(ndb.Model):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    sucursal = ndb.KeyProperty(kind=Sucursal)
    empleado = ndb.KeyProperty(kind=Empleado)
    tipo = ndb.KeyProperty(kind=TipoEgreso)
    compras = ndb.StructuredProperty(Compra,repeated=True)
    proveedor = ndb.KeyProperty(kind=Proveedor)
    total = ndb.IntegerProperty()
    resumen = ndb.TextProperty()
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
    pagada = ndb.FloatProperty()
