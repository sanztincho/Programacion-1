import os
from main import create_app, db

# Crear la aplicación con la configuración del .env
app = create_app()
app.app_context().push()

if __name__ == '__main__':
    # Crea las tablas que falten (no modifica tablas existentes: para eso están las migraciones)
    db.create_all()
    app.run(debug=True, port=int(os.getenv('PORT', 5000)))
