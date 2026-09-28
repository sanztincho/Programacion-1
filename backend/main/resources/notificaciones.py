from flask_restful import Resource
from flask import request
from .. import db
from main.models.notificaciones import Notificacion
from main.auth.decorators import role_required


class Notificaciones(Resource):

    @role_required(roles=['admin', 'empleado'])
    def get(self):
        # Obtener parámetros de consulta para filtrado
        args = request.args
        query = db.session.query(Notificacion)

        # Filtrado (por id_usuario, id_pedido, mensaje)
        if 'id_usuario' in args:
            query = query.filter(Notificacion.id_usuario == int(args['id_usuario']))
        if 'id_pedido' in args:
            query = query.filter(Notificacion.id_pedido == int(args['id_pedido']))
        if 'mensaje' in args:
            query = query.filter(Notificacion.mensaje.like(f"%{args['mensaje']}%"))

        # Paginación
        limit = int(args.get('limit', 10))  # Límite de resultados (por defecto 10)
        page = int(args.get('page', 1))     # Número de página (por defecto 1)
        offset = (page - 1) * limit         # Desplazamiento

        notificaciones = query.offset(offset).limit(limit).all()
        return [notificacion.to_json() for notificacion in notificaciones], 200

    @role_required(roles=['admin', 'empleado'])
    def post(self):
        notificacion = Notificacion.from_json(request.get_json(silent=True) or {})
        db.session.add(notificacion)
        db.session.commit()
        return notificacion.to_json(), 201
