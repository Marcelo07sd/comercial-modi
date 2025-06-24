from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo  # Nueva importación

db = SQLAlchemy()

# Función para obtener la hora de Perú (UTC-5)
def ahora_peru():
    return datetime.now(ZoneInfo("America/Lima"))

print(ahora_peru())


class Cliente(db.Model):
    __tablename__ = 'clientes'
    cliente_id = db.Column(db.Integer, primary_key=True)
    
    nombre = db.Column(db.String(15), nullable=False)
    apellido_paterno = db.Column(db.String(15), nullable=False)
    apellido_materno = db.Column(db.String(15), nullable=False)
    
    dni = db.Column(db.String(8), unique=True, nullable=False)
    
    direccion = db.Column(db.String(50))  # Nullable por si compra al contado
    referencia_direccion = db.Column(db.String(20))  # Opcional
    
    telefono_principal = db.Column(db.String(20), nullable=False)
    telefono_alternativo = db.Column(db.String(20))  # Opcional
    
    email = db.Column(db.String(40))


class Producto(db.Model):
    __tablename__ = 'productos'
    producto_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(100))
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50))


class Venta(db.Model):
    __tablename__ = 'ventas'
    venta_id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.cliente_id'), nullable=False)
    fecha_venta = db.Column(db.DateTime, nullable=False, default=ahora_peru)  # Cambiado
    tipo_pago = db.Column(db.String(20), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    cliente = db.relationship('Cliente', backref='ventas')


class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    detalle_id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.venta_id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    venta = db.relationship('Venta', backref='detalles')
    producto = db.relationship('Producto')


class Credito(db.Model):
    __tablename__ = 'creditos'
    credito_id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.venta_id'), unique=True, nullable=False)
    saldo_inicial = db.Column(db.Numeric(10, 2), nullable=False)
    saldo_actual = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    frecuencia_pago = db.Column(db.String(15), nullable=False)
    fecha_proxima_pago = db.Column(db.Date)

    venta = db.relationship('Venta')


class Pago(db.Model):
    __tablename__ = 'pagos'
    pago_id = db.Column(db.Integer, primary_key=True)
    credito_id = db.Column(db.Integer, db.ForeignKey('creditos.credito_id'), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)

    credito = db.relationship('Credito')
    

class ObservacionPago(db.Model):
    __tablename__ = 'observaciones_pago'
    observacion_id = db.Column(db.Integer, primary_key=True)
    pago_id = db.Column(db.Integer, db.ForeignKey('pagos.pago_id'), nullable=False)
    texto = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, default=ahora_peru)  # Cambiado

    pago = db.relationship('Pago', backref='observaciones')

#datetime.utcnow