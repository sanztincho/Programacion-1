from .. import jwt
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from functools import wraps


# Decorador para restringir el acceso a un recurso según el rol del usuario
def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificar que el JWT es correcto (firma válida y no expirado)
            verify_jwt_in_request()
            # Obtener los claims de adentro del JWT
            claims = get_jwt()
            # Verificar que el rol sea uno de los permitidos por la ruta
            if claims.get('rol') in roles:
                # Ejecutar la función del recurso
                return fn(*args, **kwargs)
            return {'message': 'Rol sin permisos de acceso al recurso'}, 403
        return wrapper
    return decorator


def usuario_actual():
    """Devuelve (id, rol) del usuario dueño del token. Usar dentro de un endpoint protegido."""
    return int(get_jwt_identity()), get_jwt().get('rol')


# Define el atributo que se utilizará para identificar el usuario ("sub" del token)
@jwt.user_identity_loader
def user_identity_lookup(user):
    # Definir ID como atributo identificatorio (debe ser string)
    return str(user.id)


# Define qué atributos se guardarán dentro del token (claims adicionales del payload)
@jwt.additional_claims_loader
def add_claims_to_access_token(user):
    claims = {
        'rol': user.rol,
        'id': user.id,
        'email': user.email
    }
    return claims


# Respuestas en JSON cuando hay problemas con el token (en vez de errores genéricos)
@jwt.expired_token_loader
def token_expirado(jwt_header, jwt_payload):
    return {'message': 'El token expiró, iniciá sesión nuevamente'}, 401


@jwt.invalid_token_loader
def token_invalido(motivo):
    return {'message': f'Token inválido: {motivo}'}, 401


@jwt.unauthorized_loader
def token_faltante(motivo):
    return {'message': 'Falta el token de acceso (header Authorization: Bearer <token>)'}, 401
