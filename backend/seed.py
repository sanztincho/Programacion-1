"""Carga datos de prueba: un usuario por rol y algunos productos.

Uso (con el venv activado, desde la carpeta backend):
    python3 seed.py

Es idempotente: si el usuario o el producto ya existe, no lo duplica.
"""
from main import create_app, db
from main.models import UserModel, ProductoModel

app = create_app()

USUARIOS = [
    {'nombre': 'Admin', 'apellidos': 'Rotiseria', 'email': 'admin@rotiseria.com',
     'cellphone': 2610000001, 'password': 'admin123', 'rol': 'admin', 'estado': 'activo'},
    {'nombre': 'Emilia', 'apellidos': 'Empleada', 'email': 'empleado@rotiseria.com',
     'cellphone': 2610000002, 'password': 'empleado123', 'rol': 'empleado', 'estado': 'activo'},
    {'nombre': 'Carlos', 'apellidos': 'Cliente', 'email': 'cliente@rotiseria.com',
     'cellphone': 2610000003, 'password': 'cliente123', 'rol': 'cliente', 'estado': 'activo'},
]

PRODUCTOS = [
    {'nombre': 'Milanesa napolitana', 'precio': 9500, 'categoria': 'Carnes', 'disponibilidad': 'disponible'},
    {'nombre': 'Empanadas x6', 'precio': 7200, 'categoria': 'Empanadas', 'disponibilidad': 'disponible'},
    {'nombre': 'Papas fritas', 'precio': 4000, 'categoria': 'Guarniciones', 'disponibilidad': 'disponible'},
]

with app.app_context():
    db.create_all()
    for datos in USUARIOS:
        if not db.session.query(UserModel).filter_by(email=datos['email']).first():
            db.session.add(UserModel.from_json(datos))
            print(f"Usuario creado: {datos['email']} / {datos['password']} ({datos['rol']})")
    for datos in PRODUCTOS:
        if not db.session.query(ProductoModel).filter_by(nombre=datos['nombre']).first():
            db.session.add(ProductoModel.from_json(datos))
            print(f"Producto creado: {datos['nombre']}")
    db.session.commit()
    print('Listo.')
