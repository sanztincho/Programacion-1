# Importar librerías
import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS

# Instancias globales de las extensiones (se vinculan a la app en create_app)
api = Api()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mailsender = Mail()

# Carpeta "backend" (un nivel arriba de este archivo). Sirve para resolver rutas relativas del .env
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _ruta_absoluta(ruta):
    """Convierte una ruta del .env (relativa a /backend o absoluta) en absoluta."""
    ruta = os.path.expanduser(ruta or '')
    return ruta if os.path.isabs(ruta) else os.path.join(BASE_DIR, ruta)


def _env_bool(nombre, default='False'):
    return str(os.getenv(nombre, default)).strip().lower() in ('true', '1', 'yes', 'si')


def create_app():
    # Inicializar Flask
    app = Flask(__name__)
    # Permite que los errores de JWT (401/422) lleguen al cliente aunque Flask-RESTful los intercepte
    app.config['PROPAGATE_EXCEPTIONS'] = True
    # Cargar variables de entorno desde el archivo .env
    load_dotenv(os.path.join(BASE_DIR, '.env'))

    # CORS: permite que el frontend (localhost:4200) consuma la API (localhost:5000)
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # ---------------- Base de datos ----------------
    db_dir = _ruta_absoluta(os.getenv('DATABASE_PATH', './DB/'))
    db_file = os.path.join(db_dir, os.getenv('DATABASE_NAME', 'backend.db'))
    # Crear la carpeta y el archivo de la BD si no existen
    os.makedirs(db_dir, exist_ok=True)
    if not os.path.exists(db_file):
        open(db_file, 'a').close()

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # URL de configuración de la base de datos.
    # Para cambiar de motor solo se cambia esta URL, por ejemplo:
    #   MySQL:      'mysql+pymysql://usuario:clave@localhost:3306/rotiseria'
    #   PostgreSQL: 'postgresql://usuario:clave@localhost:5432/rotiseria'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file
    db.init_app(app)
    migrate.init_app(app, db)

    # ---------------- Subida de archivos ----------------
    app.config['UPLOAD_FOLDER'] = _ruta_absoluta(os.getenv('UPLOAD_FOLDER', './uploads/'))
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_MB', 5)) * 1024 * 1024
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'valoraciones'), exist_ok=True)

    # ---------------- Recursos (endpoints REST) ----------------
    import main.resources as resources
    api.add_resource(resources.UserResource, '/user/<int:id>')
    api.add_resource(resources.UsersResource, '/users')
    api.add_resource(resources.PedidoResource, '/pedido/<int:id>')
    api.add_resource(resources.PedidosResource, '/pedidos')
    api.add_resource(resources.ValoracionesResource, '/valoraciones')
    api.add_resource(resources.ValoracionResource, '/valoracion/<int:id>')
    api.add_resource(resources.NotificacionResource, '/notificacion')
    api.add_resource(resources.ProductoResource, '/producto/<int:id>')
    api.add_resource(resources.ProductosResource, '/productos')
    api.add_resource(resources.ResumenProductoResource, '/producto/<int:id>/resumen')
    api.add_resource(resources.AsignacionResource, '/asignacion')
    api.init_app(app)

    # ---------------- JWT ----------------
    # Clave secreta con la que se firma el token
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    # Tiempo de expiración del token (segundos)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    jwt.init_app(app)

    # Blueprint de autenticación (/auth/login y /auth/register)
    from main.auth import routes
    app.register_blueprint(routes.auth)

    # ---------------- Mail ----------------
    app.config['MAIL_ENABLED'] = _env_bool('MAIL_ENABLED')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = _env_bool('MAIL_USE_TLS', 'True')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['FLASKY_MAIL_SENDER'] = os.getenv('FLASKY_MAIL_SENDER')
    mailsender.init_app(app)

    # ---------------- LLM ----------------
    app.config['LLM_ENABLED'] = _env_bool('LLM_ENABLED')
    app.config['LLM_API_URL'] = os.getenv('LLM_API_URL', '')
    app.config['LLM_API_KEY'] = os.getenv('LLM_API_KEY', '')
    app.config['LLM_MODEL'] = os.getenv('LLM_MODEL', '')
    app.config['LLM_TIMEOUT'] = int(os.getenv('LLM_TIMEOUT', 20))

    # Ruta para servir las imágenes subidas (ej: /uploads/valoraciones/abc.jpg)
    @app.route('/uploads/<path:filename>')
    def uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Error 413: archivo demasiado grande
    @app.errorhandler(413)
    def archivo_muy_grande(error):
        return {'message': f"El archivo supera el máximo de {os.getenv('MAX_UPLOAD_MB', 5)} MB"}, 413

    return app
