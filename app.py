import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Cliente, Producto, Venta, DetalleVenta, Credito, Pago, ObservacionPago, ahora_peru
from utils_pdf import generar_pdf_venta
from productos_predefinidos import cargar_productos_predefinidos

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-local')

db.init_app(app)

with app.app_context():
    db.create_all()
    cargar_productos_predefinidos()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ver-clientes')
def clientes():
    lista = Cliente.query.all()
    return render_template('ver_clientes.html', clientes=lista)



@app.route('/registrar-cliente', methods=['POST', 'GET'])
def registrar_cliente():
    if request.method == 'POST':
        dni = request.form['dni']
        cliente_existente = Cliente.query.filter_by(dni=dni).first()
        if cliente_existente:
            flash('El DNI ya está registrado. Por favor, ingrese uno diferente.', 'danger')
            return redirect(url_for('registrar_cliente'))

        nuevo_cliente = Cliente(
            nombre=request.form['nombre'],
            apellido_paterno=request.form['apellido_paterno'],
            apellido_materno=request.form['apellido_materno'],
            dni=dni,
            direccion=request.form.get('direccion'),
            referencia_direccion=request.form.get('referencia_direccion'),
            telefono_principal=request.form['telefono_principal'],
            telefono_alternativo=request.form.get('telefono_alternativo'),
            email=request.form.get('email')
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        flash('Cliente registrado con éxito.', 'success')
        return redirect(url_for('registrar_cliente'))

    return render_template('registrar_cliente.html')

# API para obtener datos de un cliente
@app.route('/api/clientes/<int:id>', methods=['GET'])
def api_obtener_cliente(id):
    cliente = Cliente.query.filter_by(cliente_id=id).first_or_404()
    return {
        'cliente_id': cliente.cliente_id,
        'nombre': cliente.nombre,
        'apellido_paterno': cliente.apellido_paterno,
        'apellido_materno': cliente.apellido_materno,
        'dni': cliente.dni,
        'direccion': cliente.direccion,
        'referencia_direccion': cliente.referencia_direccion,
        'telefono_principal': cliente.telefono_principal,
        'telefono_alternativo': cliente.telefono_alternativo,
        'email': cliente.email
    }


# API para actualizar un cliente
@app.route('/api/clientes/<int:id>', methods=['PUT'])
def api_actualizar_cliente(id):
    cliente = Cliente.query.filter_by(cliente_id=id).first_or_404()
    data = request.json

    if 'dni' in data and data['dni'] != cliente.dni:
        if Cliente.query.filter_by(dni=data['dni']).first():
            return {'error': 'El DNI ya está registrado por otro cliente.'}, 400

    cliente.nombre = data.get('nombre', cliente.nombre)
    cliente.apellido_paterno = data.get('apellido_paterno', cliente.apellido_paterno)
    cliente.apellido_materno = data.get('apellido_materno', cliente.apellido_materno)
    cliente.dni = data.get('dni', cliente.dni)
    cliente.direccion = data.get('direccion', cliente.direccion)
    cliente.referencia_direccion = data.get('referencia_direccion', cliente.referencia_direccion)
    cliente.telefono_principal = data.get('telefono_principal', cliente.telefono_principal)
    cliente.telefono_alternativo = data.get('telefono_alternativo', cliente.telefono_alternativo)
    cliente.email = data.get('email', cliente.email)

    db.session.commit()
    return {'mensaje': 'Cliente actualizado correctamente.'}


@app.route('/eliminar-cliente/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cliente = Cliente.query.filter_by(cliente_id=id).first_or_404()

    # Verificar si tiene créditos pendientes o activos
    creditos_pendientes = db.session.query(Credito).join(Venta).filter(
        Venta.cliente_id == cliente.cliente_id,
        Credito.estado.in_(['pendiente', 'activo'])
    ).count()

    if creditos_pendientes > 0:
        flash('⚠️ No se puede eliminar el cliente. Tiene créditos activos o pendientes.', 'danger')
        return redirect(url_for('clientes'))

    # Verificar si tiene ventas asociadas
    ventas_asociadas = Venta.query.filter_by(cliente_id=cliente.cliente_id).count()

    if ventas_asociadas > 0:
        flash('⚠️ No se puede eliminar el cliente. Tiene ventas registradas en el sistema.', 'danger')
        return redirect(url_for('clientes'))

    # Eliminar si no tiene ventas ni créditos pendientes
    db.session.delete(cliente)
    db.session.commit()
    flash('✅ Cliente eliminado correctamente.', 'success')
    return redirect(url_for('clientes'))


@app.route('/productos', methods=['GET', 'POST'])
def productos():
    if request.method == 'POST':
        nuevo = Producto(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion'),
            precio_unitario=request.form['precio_unitario'],
            stock=request.form['stock'],
            categoria=request.form.get('categoria')
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Producto agregado con éxito.', 'success')
        return redirect(url_for('productos'))

    lista = Producto.query.all()
    return render_template('productos.html', productos=lista)


@app.route('/productos/editar/<int:producto_id>', methods=['POST'])
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.nombre = request.form['nombre']
    producto.descripcion = request.form.get('descripcion')
    producto.precio_unitario = request.form['precio_unitario']
    producto.stock = request.form['stock']
    producto.categoria = request.form.get('categoria')
    db.session.commit()
    flash('Producto actualizado con éxito.', 'success')
    return redirect(url_for('productos'))


@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.', 'warning')
    return redirect(url_for('productos'))


@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    clientes = Cliente.query.all()
    productos = Producto.query.all()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        tipo_pago = request.form['tipo_pago']
        fecha_venta = ahora_peru()
        detalles = []

        total = 0
        for i in range(len(request.form.getlist('producto_id'))):
            producto_id = int(request.form.getlist('producto_id')[i])
            cantidad = int(request.form.getlist('cantidad')[i])
            producto = Producto.query.get(producto_id)
            precio = float(producto.precio_unitario)
            subtotal = cantidad * precio
            total += subtotal
            detalles.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio
            })

        venta = Venta(
            cliente_id=cliente_id,
            fecha_venta=fecha_venta,
            tipo_pago=tipo_pago,
            total=total
        )
        db.session.add(venta)
        db.session.flush()

        for item in detalles:
            detalle = DetalleVenta(
                venta_id=venta.venta_id,
                producto_id=item['producto'].producto_id,
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            db.session.add(detalle)

            producto = item['producto']
            if producto.stock < item['cantidad']:
                db.session.rollback()
                return f"No hay suficiente stock para {producto.nombre}", 400

            producto.stock -= item['cantidad']

        if tipo_pago.lower() == 'crédito':
            partes = list(map(int, request.form['fecha_proxima_pago'].split('-')))
            fecha_proxima_pago = ahora_peru().replace(
                year=partes[0], month=partes[1], day=partes[2],
                hour=0, minute=0, second=0
            )
            credito = Credito(
                venta_id=venta.venta_id,
                saldo_inicial=total,
                saldo_actual=total,
                estado='Pendiente',
                frecuencia_pago=request.form['frecuencia_pago'],
                fecha_proxima_pago=fecha_proxima_pago
            )
            db.session.add(credito)

        db.session.commit()

        cliente = Cliente.query.get(cliente_id)
        venta = Venta.query.get(venta.venta_id)
        detalles_db = DetalleVenta.query.filter_by(venta_id=venta.venta_id).all()

        return generar_pdf_venta(cliente, venta, detalles_db)

    ventas_historial = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    return render_template('ventas.html', clientes=clientes, productos=productos, ventas=ventas_historial)


@app.route('/detalle_venta/<int:venta_id>')
def detalle_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    detalle = {
        "exito": True,
        "cliente": f"{venta.cliente.nombre} {venta.cliente.apellido_paterno}",
        "fecha": venta.fecha_venta.strftime('%d/%m/%Y %H:%M:%S'),
        "tipo_pago": venta.tipo_pago,
        "total": float(venta.total),
        "productos": [{
            "nombre": item.producto.nombre,
            "cantidad": item.cantidad,
            "precio_unitario": float(item.precio_unitario)
        } for item in venta.detalles]
    }
    return jsonify(detalle)


@app.route('/creditos')
def ver_creditos():
    creditos = Credito.query.filter(Credito.estado != 'Pagado').all()
    return render_template('creditos.html', creditos=creditos)

@app.route('/creditos/cancelados')
def ver_creditos_cancelados():
    creditos_cancelados = Credito.query.filter(Credito.estado == 'Pagado').all()
    return render_template('creditos_cancelados.html', creditos=creditos_cancelados)



@app.route('/detalle_credito/<int:credito_id>')
def detalle_credito(credito_id):
    credito = Credito.query.get_or_404(credito_id)
    cliente = credito.venta.cliente
    detalles = DetalleVenta.query.filter_by(venta_id=credito.venta_id).all()
    pagos = Pago.query.filter_by(credito_id=credito_id).order_by(Pago.fecha_pago.asc()).all()

    productos = [{
        "nombre": d.producto.nombre,
        "cantidad": d.cantidad,
        "precio_unitario": float(d.precio_unitario)
    } for d in detalles]

    lista_pagos = []
    for p in pagos:
        observaciones = [{
            "texto": o.texto,
            "fecha": o.fecha.strftime('%H:%M')
        } for o in p.observaciones]
        lista_pagos.append({
            "fecha": p.fecha_pago.strftime('%d-%m-%Y'),
            "monto": float(p.monto),
            "observaciones": observaciones
        })

    return jsonify({
        "exito": True,
        "cliente": f"{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}",
        "direccion": cliente.direccion,
        "telefono": cliente.telefono_principal,
        "productos": productos,
        "pagos": lista_pagos,
        "saldo_actual": float(credito.saldo_actual),
        "saldo_inicial": float(credito.saldo_inicial)
    })


@app.route('/agregar_pago/<int:credito_id>', methods=['POST'])
def agregar_pago(credito_id):
    credito = Credito.query.get_or_404(credito_id)

    try:
        data = request.json
        monto = float(data['monto'])
        textos_obs = data.get('observaciones', [])
    except (ValueError, KeyError):
        return jsonify({"exito": False, "mensaje": "Datos inválidos"})

    nuevo_saldo = float(credito.saldo_actual) - monto
    nuevo_saldo = max(nuevo_saldo, 0)

    nuevo_pago = Pago(
        credito_id=credito_id,
        fecha_pago=ahora_peru().date(),
        monto=monto
    )
    db.session.add(nuevo_pago)
    db.session.flush()

    for texto in textos_obs:
        obs = ObservacionPago(
            pago_id=nuevo_pago.pago_id,
            texto=texto,
            fecha=ahora_peru()
        )
        db.session.add(obs)

    credito.saldo_actual = nuevo_saldo
    if nuevo_saldo == 0:
        credito.estado = 'Pagado'

    db.session.commit()

    return jsonify({
        "exito": True,
        "saldo_actual": nuevo_saldo
    })


# ===== BACKEND Flask - Editar Pago =====

@app.route('/editar_pago/<int:pago_id>', methods=['PUT'])
def editar_pago(pago_id):
    pago = Pago.query.get_or_404(pago_id)

    try:
        data = request.json
        monto = float(data['monto'])
        textos_obs = data.get('observaciones', [])
    except (ValueError, KeyError):
        return jsonify({"exito": False, "mensaje": "Datos inválidos"})

    credito = Credito.query.get(pago.credito_id)

    # Recalcular saldo actual
    saldo_actual = float(credito.saldo_inicial)
    otros_pagos = Pago.query.filter(Pago.credito_id == credito.credito_id, Pago.pago_id != pago_id).all()

    for p in otros_pagos:
        saldo_actual -= float(p.monto)

    saldo_actual -= monto
    saldo_actual = max(saldo_actual, 0)

    # Actualizar monto del pago y saldo
    pago.monto = monto

    # Eliminar observaciones anteriores
    ObservacionPago.query.filter_by(pago_id=pago.pago_id).delete()

    for texto in textos_obs:
        nueva_obs = ObservacionPago(
            pago_id=pago.pago_id,
            texto=texto,
            fecha=ahora_peru()
        )
        db.session.add(nueva_obs)

    credito.saldo_actual = saldo_actual
    if saldo_actual <= 0:
        credito.estado = "Pagado"
    else:
        credito.estado = "Pendiente"

    db.session.commit()

    return jsonify({"exito": True, "saldo_actual": saldo_actual})
