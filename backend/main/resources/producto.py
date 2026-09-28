from flask_restful import Resource
from flask import request
from sqlalchemy import func
from .. import db
from main.models import ProductoModel, PedidoModel, ValoracionModel
from main.auth.decorators import role_required
from main.llm.functions import resumir_resenas

CAMPOS_EDITABLES = {'nombre', 'precio', 'categoria', 'disponibilidad'}


class Producto(Resource):
    def get(self, id):
        producto = db.session.get(ProductoModel, id) or _no_encontrado()
        return producto.to_json(), 200

    @role_required(roles=["admin", "empleado"])
    def put(self, id):
        producto = db.session.get(ProductoModel, id) or _no_encontrado()
        data = request.get_json(silent=True) or {}
        # Solo se actualizan los campos permitidos (se ignoran id, promedio, etc.)
        for key, value in data.items():
            if key in CAMPOS_EDITABLES:
                setattr(producto, key, value)
        db.session.add(producto)
        db.session.commit()
        return producto.to_json(), 200

    @role_required(roles=["admin"])
    def delete(self, id):
        producto = db.session.get(ProductoModel, id) or _no_encontrado()
        db.session.delete(producto)
        db.session.commit()
        return '', 204


class Productos(Resource):
    def get(self):
        # Subconsulta: promedio y cantidad de valoraciones por producto
        #   SELECT id_producto, AVG(puntuacion) AS promedio, COUNT(id) AS cantidad
        #   FROM valoracion GROUP BY id_producto
        stats = (
            db.session.query(
                ValoracionModel.id_producto.label('id_producto'),
                func.avg(ValoracionModel.puntuacion).label('promedio'),
                func.count(ValoracionModel.id).label('cantidad')
            )
            .group_by(ValoracionModel.id_producto)
            .subquery()
        )
        # LEFT OUTER JOIN para no perder los productos que todavía no tienen reseñas
        query = db.session.query(ProductoModel).outerjoin(stats, ProductoModel.id == stats.c.id_producto)

        # ---------- Filtros ----------
        nombre = request.args.get('nombre')
        if nombre:
            query = query.filter(ProductoModel.nombre.ilike(f'%{nombre}%'))

        precio_min = request.args.get('precio_min')
        if precio_min:
            query = query.filter(ProductoModel.precio >= float(precio_min))

        precio_max = request.args.get('precio_max')
        if precio_max:
            query = query.filter(ProductoModel.precio <= float(precio_max))

        categoria = request.args.get('categoria')
        if categoria:
            query = query.filter(ProductoModel.categoria.ilike(f'%{categoria}%'))

        disponibilidad = request.args.get('disponibilidad')
        if disponibilidad:
            query = query.filter(ProductoModel.disponibilidad == disponibilidad)

        # Filtro por calificación: promedio de estrellas mayor o igual a valoracion_min (1 a 5)
        valoracion_min = request.args.get('valoracion_min')
        if valoracion_min:
            query = query.filter(stats.c.promedio >= float(valoracion_min))

        # ---------- Ordenamiento ----------
        orden = request.args.get('orden')
        if orden == 'valoracion':
            # Mejor calificados primero; los que no tienen reseñas quedan al final
            query = query.order_by(stats.c.promedio.is_(None), stats.c.promedio.desc(),
                                   stats.c.cantidad.desc())
        elif orden == 'precio_asc':
            query = query.order_by(ProductoModel.precio.asc())
        elif orden == 'precio_desc':
            query = query.order_by(ProductoModel.precio.desc())
        else:
            query = query.order_by(ProductoModel.id)

        # ---------- Paginación ----------
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'productos': [producto.to_json() for producto in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'page': pagination.page
        }, 200

    @role_required(roles=["admin"])
    def post(self):
        data = request.get_json(silent=True) or {}
        if not data.get('nombre') or data.get('precio') in (None, ''):
            return {'message': 'nombre y precio son obligatorios'}, 400

        # Crear el producto desde los datos JSON
        producto = ProductoModel.from_json(data)
        if not producto.categoria:
            producto.categoria = 'General'

        # Si hay pedidos asociados (opcional)
        pedido_ids = data.get('pedidos')
        if pedido_ids:
            pedidos = PedidoModel.query.filter(PedidoModel.id.in_(pedido_ids)).all()
            producto.pedidos.extend(pedidos)

        db.session.add(producto)
        db.session.commit()
        return producto.to_json(), 201


class ResumenProducto(Resource):
    """GET /producto/<id>/resumen -> resumen de las reseñas generado por un LLM."""

    def get(self, id):
        producto = db.session.get(ProductoModel, id) or _no_encontrado()
        resenas = [v for v in producto.valoracion if v.puntuacion is not None]
        resultado = resumir_resenas(producto.nombre, resenas)
        return {
            'id_producto': producto.id,
            'producto': producto.nombre,
            'promedio_valoracion': producto.promedio_valoracion,
            'cantidad_valoraciones': len(resenas),
            **resultado  # resumen + fuente ('llm' o 'estadistico')
        }, 200


def _no_encontrado():
    from flask_restful import abort
    abort(404, message='Producto no encontrado')
