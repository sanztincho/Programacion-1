from flask_restful import Resource
from flask import request
from .. import db
from main.models import UserModel
from sqlalchemy import or_
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.auth.decorators import role_required, usuario_actual

# Campos que cada rol puede modificar con PUT /user/<id>
CAMPOS_PROPIOS = {'nombre', 'apellidos', 'email', 'cellphone', 'password'}
CAMPOS_EMPLEADO = {'estado'}
CAMPOS_ADMIN = CAMPOS_PROPIOS | {'estado', 'rol'}
ROLES_VALIDOS = {'admin', 'empleado', 'cliente'}
ESTADOS_VALIDOS = {'activo', 'pendiente', 'bloqueado'}


class User(Resource):
    @jwt_required(optional=True)
    def get(self, id):
        user = db.session.get(UserModel, id) or _no_encontrado()
        current_identity = get_jwt_identity()
        # El propio usuario recibe también sus pedidos
        if str(current_identity) == str(user.id):
            return user.to_json_complete()
        return user.to_json()

    @jwt_required()
    def put(self, id):
        user = db.session.get(UserModel, id) or _no_encontrado()
        id_actual, rol = usuario_actual()
        data = request.get_json(silent=True) or {}

        # ¿Qué campos puede tocar quien hace la petición?
        if rol == 'admin':
            permitidos = CAMPOS_ADMIN
        elif id_actual == user.id:
            permitidos = CAMPOS_PROPIOS
        elif rol == 'empleado' and user.rol == 'cliente':
            # El empleado solo valida o bloquea clientes
            permitidos = CAMPOS_EMPLEADO
        else:
            return {'message': 'No tenés permisos para modificar este usuario'}, 403

        no_permitidos = set(data) - permitidos - {'id'}
        if no_permitidos:
            return {'message': f"No podés modificar: {', '.join(sorted(no_permitidos))}"}, 403

        if 'rol' in data and data['rol'] not in ROLES_VALIDOS:
            return {'message': f"Rol inválido. Opciones: {', '.join(sorted(ROLES_VALIDOS))}"}, 400
        if 'estado' in data and data['estado'] not in ESTADOS_VALIDOS:
            return {'message': f"Estado inválido. Opciones: {', '.join(sorted(ESTADOS_VALIDOS))}"}, 400
        if 'email' in data and data['email'] != user.email:
            existe = db.session.query(UserModel).filter(UserModel.email == data['email']).first()
            if existe:
                return {'message': 'El email ya está en uso'}, 409

        for key, value in data.items():
            if key == 'id':
                continue
            if key == 'password':
                # Nunca se guarda la contraseña en texto plano: el setter calcula el hash
                user.plain_password = value
            else:
                setattr(user, key, value)
        db.session.add(user)
        db.session.commit()
        return user.to_json(), 200

    @role_required(roles=["admin", "cliente"])
    def delete(self, id):
        user = db.session.get(UserModel, id) or _no_encontrado()
        id_actual, rol = usuario_actual()
        # Un cliente solo puede eliminar su propia cuenta
        if rol == 'cliente' and user.id != id_actual:
            return {'message': 'No tenés permisos para eliminar este usuario'}, 403
        db.session.delete(user)
        db.session.commit()
        return '', 204


class Users(Resource):
    @role_required(roles=["admin", "empleado"])
    def get(self):
        # Obtener parámetros de consulta (query params) para filtrado
        args = request.args
        query = db.session.query(UserModel)

        # Filtrado por nombre y/o apellidos
        nombre_filter = None
        apellidos_filter = None
        if 'nombre' in args:
            nombre_filter = UserModel.nombre.like(f"%{args['nombre']}%")
        if 'apellidos' in args:
            apellidos_filter = UserModel.apellidos.like(f"%{args['apellidos']}%")

        # Si llegan los dos con el mismo texto (buscador único), se usa OR
        if nombre_filter is not None and apellidos_filter is not None:
            if args.get('nombre') == args.get('apellidos'):
                query = query.filter(or_(nombre_filter, apellidos_filter))
            else:
                query = query.filter(nombre_filter).filter(apellidos_filter)
        elif nombre_filter is not None:
            query = query.filter(nombre_filter)
        elif apellidos_filter is not None:
            query = query.filter(apellidos_filter)

        # Filtrado por email
        if 'email' in args:
            query = query.filter(UserModel.email.like(f"%{args['email']}%"))
        # Filtrado por rol y por estado
        if 'rol' in args:
            query = query.filter(UserModel.rol == args['rol'])
        if 'estado' in args:
            query = query.filter(UserModel.estado == args['estado'])

        # Paginación con offset/limit
        limit = int(args.get('limit', 10))  # Límite de resultados (por defecto 10)
        page = int(args.get('page', 1))     # Número de página (por defecto 1)
        offset = (page - 1) * limit         # Cuántos registros saltear

        users = query.order_by(UserModel.id).offset(offset).limit(limit).all()
        return [user.to_json() for user in users], 200

    @role_required(roles=["admin"])
    def post(self):
        data = request.get_json(silent=True) or {}
        if db.session.query(UserModel).filter(UserModel.email == data.get('email')).first():
            return {'message': 'Duplicated mail'}, 409
        user = UserModel.from_json(data)
        db.session.add(user)
        db.session.commit()
        return user.to_json(), 201


def _no_encontrado():
    from flask_restful import abort
    abort(404, message='Usuario no encontrado')
