import os
import uuid
from flask_restful import Resource
from flask import request, current_app
from flask_jwt_extended import jwt_required
from .. import db
from main.models import ValoracionModel, ProductoModel
from main.auth.decorators import usuario_actual

EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _guardar_imagen(archivo):
    """Guarda la imagen en uploads/valoraciones con un nombre único y devuelve la ruta relativa."""
    extension = archivo.filename.rsplit('.', 1)[-1].lower() if '.' in archivo.filename else ''
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValueError(f"Formato no permitido. Usá: {', '.join(sorted(EXTENSIONES_PERMITIDAS))}")
    if not (archivo.mimetype or '').startswith('image/'):
        raise ValueError('El archivo no es una imagen')
    # uuid evita choques de nombres y que alguien pise archivos ajenos
    nombre = f'{uuid.uuid4().hex}.{extension}'
    archivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'valoraciones', nombre))
    return f'valoraciones/{nombre}'


def _borrar_imagen(ruta_relativa):
    if ruta_relativa:
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], ruta_relativa)
        if os.path.isfile(ruta):
            os.remove(ruta)


class Valoracion(Resource):
    def get(self, id):
        valoracion = db.session.get(ValoracionModel, id) or _no_encontrada()
        return valoracion.to_json(), 200

    @jwt_required()
    def delete(self, id):
        valoracion = db.session.get(ValoracionModel, id) or _no_encontrada()
        id_actual, rol = usuario_actual()
        # La borra el autor o un admin
        if rol != 'admin' and valoracion.id_usuario != id_actual:
            return {'message': 'No tenés permisos para eliminar esta reseña'}, 403
        _borrar_imagen(valoracion.imagen)
        db.session.delete(valoracion)
        db.session.commit()
        return '', 204


class Valoraciones(Resource):
    def get(self):
        # Obtener parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        id_usuario = request.args.get('id_usuario')
        id_producto = request.args.get('id_producto')
        puntuacion = request.args.get('puntuacion')
        con_imagen = request.args.get('con_imagen')

        # Armar la consulta
        query = db.session.query(ValoracionModel)
        if id_usuario:
            query = query.filter(ValoracionModel.id_usuario == int(id_usuario))
        if id_producto:
            query = query.filter(ValoracionModel.id_producto == int(id_producto))
        if puntuacion:
            query = query.filter(ValoracionModel.puntuacion == int(puntuacion))
        if con_imagen == 'true':
            query = query.filter(ValoracionModel.imagen.isnot(None))

        # Más recientes primero + paginación
        query = query.order_by(ValoracionModel.id.desc())
        valoraciones_paginadas = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'valoraciones': [v.to_json() for v in valoraciones_paginadas.items],
            'total': valoraciones_paginadas.total,
            'pages': valoraciones_paginadas.pages,
            'page': valoraciones_paginadas.page
        }, 200

    @jwt_required()
    def post(self):
        """Crea una reseña. Acepta JSON o multipart/form-data (este último permite adjuntar 'imagen')."""
        id_actual, _ = usuario_actual()
        # request.form = campos de texto de un form-data; request.get_json = cuerpo JSON
        data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

        try:
            puntuacion = int(data.get('puntuacion', 0))
            id_producto = int(data.get('id_producto', 0))
        except ValueError:
            return {'message': 'puntuacion e id_producto deben ser números'}, 400
        if not 1 <= puntuacion <= 5:
            return {'message': 'La puntuación debe estar entre 1 y 5'}, 400
        if not db.session.get(ProductoModel, id_producto):
            return {'message': 'El producto no existe'}, 404

        valoracion = ValoracionModel.from_json({
            'puntuacion': puntuacion,
            'id_producto': id_producto,
            'comentario': (data.get('comentario') or '')[:255],
            'id_usuario': id_actual  # el autor sale del token, no del cuerpo
        })

        # Imagen opcional (campo "imagen" del form-data)
        archivo = request.files.get('imagen')
        if archivo and archivo.filename:
            try:
                valoracion.imagen = _guardar_imagen(archivo)
            except ValueError as error:
                return {'message': str(error)}, 400

        db.session.add(valoracion)
        db.session.commit()
        return valoracion.to_json(), 201


def _no_encontrada():
    from flask_restful import abort
    abort(404, message='Valoración no encontrada')
