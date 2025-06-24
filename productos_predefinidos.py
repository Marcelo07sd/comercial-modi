from models import db, Producto

def cargar_productos_predefinidos():
    if Producto.query.count() == 0:
        productos_predefinidos = [
            {
                "nombre": "Librero Pequeño",
                "precio_unitario": 120,
                "descripcion": "Librero compacto ideal para espacios reducidos.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Librero de Cómputo",
                "precio_unitario": 180,
                "descripcion": "Librero con espacio para equipos de cómputo y libros.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Librero Grande",
                "precio_unitario": 250,
                "descripcion": "Librero amplio con múltiples niveles.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Mesa de Sala",
                "precio_unitario": 200,
                "descripcion": "Mesa central para sala de estar.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Mesa de Cómputo",
                "precio_unitario": 160,
                "descripcion": "Mesa ergonómica para uso con computadora.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Mesa para TV",
                "precio_unitario": 180,
                "descripcion": "Mesa baja para colocar televisor y equipos multimedia.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Cómoda Pequeña",
                "precio_unitario": 140,
                "descripcion": "Cómoda de tamaño reducido con cajones.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Cómoda Grande",
                "precio_unitario": 220,
                "descripcion": "Cómoda espaciosa con múltiples compartimientos.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Cómoda con Espejo",
                "precio_unitario": 260,
                "descripcion": "Cómoda con espejo ideal para dormitorio.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Ropero Junior",
                "precio_unitario": 280,
                "descripcion": "Ropero compacto para habitación infantil.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Ropero Grande",
                "precio_unitario": 350,
                "descripcion": "Ropero grande con divisiones internas.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Ropero con Espejo",
                "precio_unitario": 390,
                "descripcion": "Ropero grande con espejo incorporado.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Repostero Metálico Pequeño",
                "precio_unitario": 170,
                "descripcion": "Repostero metálico pequeño para cocina.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Repostero Metálico Grande",
                "precio_unitario": 250,
                "descripcion": "Repostero metálico grande y resistente.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Repostero Melamine Pequeño",
                "precio_unitario": 200,
                "descripcion": "Repostero melamine pequeño con estantes.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Repostero Melamine Grande",
                "precio_unitario": 280,
                "descripcion": "Repostero grande de melamine.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Colchón Sueños plaza y media",
                "precio_unitario": 320,
                "descripcion": "Colchón marca Sueños para plaza y media.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Dormitel plaza y media",
                "precio_unitario": 300,
                "descripcion": "Colchón Dormitel cómodo y económico.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Sueños 2 plazas",
                "precio_unitario": 420,
                "descripcion": "Colchón Sueños de 2 plazas de alta durabilidad.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Dormitel 2 plazas",
                "precio_unitario": 390,
                "descripcion": "Colchón Dormitel tamaño 2 plazas.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Paraíso",
                "precio_unitario": 500,
                "descripcion": "Colchón Paraíso ortopédico.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Zapatero",
                "precio_unitario": 120,
                "descripcion": "Zapatero práctico para organizar calzado.",
                "categoria": "Accesorios"
            },
            {
                "nombre": "Zapatero con Espejo",
                "precio_unitario": 180,
                "descripcion": "Zapatero vertical con espejo frontal.",
                "categoria": "Accesorios"
            },
            {
                "nombre": "Estante Multiuso",
                "precio_unitario": 130,
                "descripcion": "Estante para múltiples usos domésticos.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Perchero",
                "precio_unitario": 90,
                "descripcion": "Perchero de pie para ropa y accesorios.",
                "categoria": "Accesorios"
            }
        ]

        for producto in productos_predefinidos:
            db.session.add(Producto(
                nombre=producto["nombre"],
                descripcion=producto["descripcion"],
                precio_unitario=producto["precio_unitario"],
                stock=20,
                categoria=producto["categoria"]
            ))

        db.session.commit()