from flask_restful import Resource
from flask import request
from .. import db
from main.models import PedidosProductosModel, PedidoModel, ProductoModel
from main.auth.decorators import role_required


class Asignacion(Resource):
    """POST /asignacion -> agrega un producto a un pedido (inserta en la tabla intermedia)."""

    @role_required(roles=['admin', 'empleado'])
    def post(self):
        data = request.get_json(silent=True) or {}
        id_pedido = data.get('id_pedido')
        id_producto = data.get('id_producto')

        if not db.session.get(PedidoModel, id_pedido or 0):
            return {'message': 'El pedido no fue encontrado'}, 404
        if not db.session.get(ProductoModel, id_producto or 0):
            return {'message': 'El producto no fue encontrado'}, 404

        # Las columnas de la tabla intermedia se llaman pedido_id y producto_id
        query = PedidosProductosModel.insert().values(pedido_id=id_pedido, producto_id=id_producto)
        try:
            db.session.execute(query)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {'message': 'Ese producto ya está asignado a ese pedido'}, 409
        return {'message': 'Asignación creada'}, 201
