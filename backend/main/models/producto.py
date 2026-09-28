from .. import db


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    disponibilidad = db.Column(db.String(50), nullable=False)

    # Relación 1 a N: un producto tiene muchas valoraciones.
    # Si se borra el producto, se borran sus valoraciones (cascade).
    valoracion = db.relationship('Valoracion', back_populates='producto', lazy=True,
                                 cascade='all, delete-orphan')
    # La relación N a N con Pedido se define en pedidos.py (backref 'pedidos')

    def __repr__(self):
        return '<Producto %r>' % self.nombre

    @property
    def promedio_valoracion(self):
        """Promedio de estrellas del producto (None si no tiene reseñas)."""
        puntajes = [v.puntuacion for v in self.valoracion if v.puntuacion is not None]
        return round(sum(puntajes) / len(puntajes), 2) if puntajes else None

    def to_json(self):
        producto_json = {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'categoria': self.categoria,
            'disponibilidad': self.disponibilidad,
            'promedio_valoracion': self.promedio_valoracion,
            'cantidad_valoraciones': len(self.valoracion)
        }
        return producto_json

    @staticmethod
    def from_json(producto_json):
        id = producto_json.get('id')
        nombre = producto_json.get('nombre')
        precio = producto_json.get('precio')
        categoria = producto_json.get('categoria')
        disponibilidad = producto_json.get('disponibilidad', 'disponible')
        return Producto(id=id, nombre=nombre, precio=precio, categoria=categoria,
                        disponibilidad=disponibilidad)
