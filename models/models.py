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

class Remision(ndb.Model):
    numero = ndb.IntegerProperty()
    cliente = ndb.KeyProperty(kind=Cliente)
    empleado = ndb.KeyProperty(kind=Empleado)
    fecha = ndb.DateProperty()
    ventas = ndb.StructuredProperty(Venta,repeated=True)
    total = ndb.IntegerProperty()
    anulada = ndb.BooleanProperty(default=False)
    
class Factura(ndb.Model):
    numero = ndb.IntegerProperty()
    cliente = ndb.KeyProperty(kind=Cliente)
    empleado = ndb.KeyProperty(kind=Empleado)
    fecha = ndb.DateProperty()
    ventas = ndb.StructuredProperty(Venta,repeated=True)
    total = ndb.IntegerProperty()
    anulada = ndb.BooleanProperty(default=False)

########## EGRESOS #######

class TipoEgreso(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Proveedor(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
    diasPago = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)
    bienesoservicios = ndb.KeyProperty(kind="Bienoservicio", repeated=True) 

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

class Egreso(ndb.Model):
    numero = ndb.IntegerProperty()
    fecha = ndb.DateProperty()
    empleado = ndb.KeyProperty(kind=Empleado)
    tipo = ndb.KeyProperty(kind=TipoEgreso)
    compras = ndb.StructuredProperty(Compra,repeated=True)
    proveedor = ndb.KeyProperty(kind=Proveedor)
    total = ndb.IntegerProperty()
    detalle = ndb.TextProperty()

    

    
    