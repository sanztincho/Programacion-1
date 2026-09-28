from flask_restful import Resource
from flask import request
from datetime import datetime
from .. import db
from main.models import PedidoModel, ProductoModel, ESTADOS_PEDIDO
from flask_jwt_extended import jwt_required
from main.auth.decorators import role_required, usuario_actual

ROLES_PERSONAL = ['admin', 'empleado']


def _normalizar_estado(estado):
    """Quita espacios y respeta mayúsculas de la lista oficial (' listo ' -> 'Listo')."""
    limpio = (estado or '').strip()
    for valido in ESTADOS_PEDIDO:
        if limpio.lower() == valido.lower():
            return valido
    return None


class Pedido(Resource):
    @jwt_required()
    def get(self, id):
        pedido = db.session.get(PedidoModel, id) or _no_encontrado()
        id_actual, rol = usuario_actual()
        # Un cliente solo puede ver sus propios pedidos
        if rol not in ROLES_PERSONAL and pedido.id_user != id_actual:
            return {'message': 'No tenés permisos para ver este pedido'}, 403
        return pedido.to_json(), 200

    @role_required(roles=['admin'])
    def delete(self, id):
        pedido = db.session.get(PedidoModel, id) or _no_encontrado()
        db.session.delete(pedido)
        db.session.commit()
        return '', 204

    @role_required(roles=ROLES_PERSONAL)
    def put(self, id):
        pedido = db.session.get(PedidoModel, id) or _no_encontrado()
        data = request.get_json(silent=True) or {}
        try:
            for key, value in data.items():
                if key == 'fecha':
                    # Convertir string de fecha a datetime
                    if isinstance(value, str):
                        try:
                            if 'T' in value:
                                # Formato ISO con hora (2025-10-28T18:22:24)
                                fecha_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            else:
                                # Formato solo fecha (YYYY-MM-DD)
                                fecha_obj = datetime.strptime(value, '%Y-%m-%d')
                            pedido.fecha = fecha_obj
                        except ValueError as e:
                            return {'message': f'Formato de fecha inválido: {e}'}, 400
                elif key == 'estado':
                    estado = _normalizar_estado(value)
                    if not estado:
                        return {'message': f"Estado inválido. Opciones: {', '.join(ESTADOS_PEDIDO)}"}, 400
                    pedido.estado = estado
                elif key in ('precio_final', 'id_user'):
                    setattr(pedido, key, value)
                # 'productos' se maneja abajo; cualquier otra clave se ignora

            # Si se pasan productos, se reemplaza la relación N a N
            producto_ids = data.get('productos')
            if producto_ids is not None:
                pedido.productos = ProductoModel.query.filter(ProductoModel.id.in_(producto_ids)).all()

            db.session.add(pedido)
            db.session.commit()
            return pedido.to_json(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500


class Pedidos(Resource):
    @jwt_required()
    def get(self):
        id_actual, rol = usuario_actual()
        query = db.session.query(PedidoModel)

        # ---------- Filtros ----------
        estado = request.args.get('estado')
        if estado:
            query = query.filter(PedidoModel.estado.ilike(f'%{estado.strip()}%'))

        id_user = request.args.get('id_user')
        if rol not in ROLES_PERSONAL:
            # El cliente siempre ve solo sus pedidos, aunque mande otro id_user
            query = query.filter(PedidoModel.id_user == id_actual)
        elif id_user:
            query = query.filter(PedidoModel.id_user == int(id_user))

        fecha = request.args.get('fecha')  # YYYY-MM-DD
        if fecha:
            query = query.filter(db.func.date(PedidoModel.fecha) == fecha)

        # Más recientes primero
        query = query.order_by(PedidoModel.fecha.desc())

        # ---------- Paginación ----------
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'pedidos': [pedido.to_json() for pedido in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'page': pagination.page
        }, 200

    @jwt_required()
    def post(self):
        id_actual, rol = usuario_actual()
        data = request.get_json(silent=True) or {}

        producto_ids = data.get('productos') or []
        if not producto_ids:
            return {'message': 'El pedido debe tener al menos un producto'}, 400

        try:
            pedido = PedidoModel.from_json(data)
            # El dueño del pedido sale del token (un cliente no puede crear pedidos a nombre de otro)
            if rol not in ROLES_PERSONAL or not pedido.id_user:
                pedido.id_user = id_actual
            pedido.estado = _normalizar_estado(pedido.estado) or 'Pendiente'

            productos = ProductoModel.query.filter(ProductoModel.id.in_(producto_ids)).all()
            if not productos:
                return {'message': 'Ninguno de los productos existe'}, 400
            pedido.productos.extend(productos)
            # Si no mandan el total, se calcula con los precios de la BD
            if not pedido.precio_final:
                pedido.precio_final = int(sum(p.precio for p in productos))

            db.session.add(pedido)
            db.session.commit()
            return pedido.to_json(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500


def _no_encontrado():
    from flask_restful import abort
    abort(404, message='Pedido no encontrado')
