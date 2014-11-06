from google.appengine.ext import ndb

class Cliente(ndb.Model):
    """Models an individual Client."""
    nombre = ndb.StringProperty(indexed=True)
    negocio = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
    diasPago = ndb.IntegerProperty()
    rotulo = ndb.ComputedProperty(lambda self: self.nombre +' '+ self.negocio)
    
class Fruta(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: self.nombre)

class Porcion(ndb.Model):
    valor = ndb.IntegerProperty()
    unidades = ndb.StringProperty(indexed=True)
    rotulo = ndb.ComputedProperty(lambda self: str(self.valor) + self.unidades)
    

class Precio(ndb.Model):
    fruta = ndb.KeyProperty(kind=Fruta)
    porcion = ndb.KeyProperty(kind=Porcion)
    cliente = ndb.KeyProperty(kind=Cliente)
    precio = ndb.IntegerProperty()
    
class Venta(ndb.Model):
    fruta = ndb.KeyProperty(kind=Fruta)
    porcion = ndb.KeyProperty(kind=Porcion)
    cantidad = ndb.IntegerProperty()
    precio = ndb.IntegerProperty()
    venta = ndb.IntegerProperty()

class NumeroFactura(ndb.Model):
    consecutivo = ndb.IntegerProperty()
    
class Factura(ndb.Model):
    numero = ndb.IntegerProperty()
    cliente = ndb.KeyProperty(kind=Cliente)
    fecha = ndb.DateProperty()
    ventas = ndb.StructuredProperty(Venta,repeated=True)
    total = ndb.IntegerProperty()
    