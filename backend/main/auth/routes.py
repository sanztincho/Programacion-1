from flask import request, Blueprint, current_app
from .. import db
from main.models import UserModel
from flask_jwt_extended import create_access_token
from main.mail.functions import sendMail

auth = Blueprint("auth", __name__, url_prefix="/auth")


# Método de logueo
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return {'message': 'Faltan email o password'}, 400

    user = db.session.query(UserModel).filter(UserModel.email == email).first()
    # Devolver error si no existe el usuario o si la contraseña no es correcta
    if (user is None) or not user.validate_pass(password):
        return {'message': 'Usuario o contraseña incorrectos'}, 401

    # Un usuario bloqueado por el personal no puede ingresar
    if (user.estado or '').lower() == 'bloqueado':
        return {'message': 'Tu cuenta está bloqueada. Contactá a la rotisería.'}, 403

    # Genera un nuevo token pasando el objeto user como identidad
    # (los decoradores de auth/decorators.py definen qué va dentro del token)
    access_token = create_access_token(identity=user)

    # Devolver valores y token (data NO es el payload del token: es la respuesta del login)
    data = {
        'id': str(user.id),
        'email': user.email,
        'rol': user.rol,
        'nombre': user.nombre,
        'access_token': access_token
    }
    return data, 200


# Método de registro (siempre crea clientes: el rol no se puede elegir desde afuera)
@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    obligatorios = ['nombre', 'apellidos', 'email', 'cellphone', 'password']
    faltantes = [campo for campo in obligatorios if not data.get(campo)]
    if faltantes:
        return {'message': f"Faltan campos: {', '.join(faltantes)}"}, 400

    # Se ignora cualquier "rol" o "estado" enviado: un cliente nuevo queda pendiente de validación
    data = {**data, 'rol': 'cliente', 'estado': 'pendiente'}
    user = UserModel.from_json(data)

    # Verificar si el mail ya existe en la BD
    exists = db.session.query(UserModel).filter(UserModel.email == user.email).scalar() is not None
    if exists:
        return {'message': 'Duplicated mail'}, 409

    try:
        # Agregar usuario a la BD
        db.session.add(user)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return {'message': str(error)}, 409

    # Enviar mail de bienvenida (si falla, el registro igual es válido)
    if current_app.config.get('MAIL_ENABLED'):
        try:
            sendMail([user.email], "¡Bienvenido/a!", 'register', user=user)
        except Exception as mail_error:
            current_app.logger.warning(f'No se pudo enviar el mail: {mail_error}')

    return user.to_json(), 201
