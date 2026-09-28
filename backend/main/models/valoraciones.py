from .. import db


class Valoracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'))
    puntuacion = db.Column(db.Integer)
    comentario = db.Column(db.String(255))
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id'))
    # Ruta relativa de la imagen adjunta (ej: "valoraciones/3f2a...jpg"). Es opcional.
    imagen = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', back_populates='valoraciones')  # relación con la tabla User
    producto = db.relationship('Producto', back_populates='valoracion')  # relación con la tabla Producto

    def __repr__(self):
        return '<Valoracion %r: %r estrellas>' % (self.id, self.puntuacion)

    def to_json(self):
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'id_producto': self.id_producto,
            'puntuacion': self.puntuacion,
            'comentario': self.comentario,
            # La URL es relativa al servidor: el frontend le antepone la URL de la API
            'imagen': f'/uploads/{self.imagen}' if self.imagen else None,
            'user': self.user.to_json() if self.user else None,
            'producto': self.producto.to_json() if self.producto else None
        }

    @staticmethod
    # convierto json (o form-data) a objeto
    def from_json(valoraciones_json):
        id = valoraciones_json.get('id')
        id_usuario = valoraciones_json.get('id_usuario')
        puntuacion = valoraciones_json.get('puntuacion')
        comentario = valoraciones_json.get('comentario')
        id_producto = valoraciones_json.get('id_producto')
        return Valoracion(id=id, id_usuario=id_usuario, puntuacion=puntuacion,
                          comentario=comentario, id_producto=id_producto)
