# Programación 1 — La Rotisería (proyecto anual grupal)

Aplicación web para una rotisería: los **clientes** ven el menú, lo filtran por calificación, arman pedidos y dejan reseñas con foto; los **empleados** gestionan el stock, el estado de los pedidos y validan usuarios; el **administrador** gestiona productos, pedidos y usuarios.

- **Backend:** Flask + Flask-RESTful + SQLAlchemy (SQLite) + JWT — carpeta `backend/`
- **Frontend:** Angular 20 (componentes standalone) + Bootstrap 5 — carpeta `frontend/app_rotiseria/`

## Puesta en marcha rápida

```bash
# Backend (terminal 1)
cd backend
chmod +x install.sh boot.sh
./install.sh          # crea venv, instala requirements y crea .env desde .env-example
source venv/bin/activate && python3 seed.py   # usuarios y productos de prueba
./boot.sh             # API en http://localhost:5000

# Frontend (terminal 2)
cd frontend/app_rotiseria
npm install
npx ng serve          # web en http://localhost:4200
```

Usuarios de prueba: `admin@rotiseria.com / admin123`, `empleado@rotiseria.com / empleado123`, `cliente@rotiseria.com / cliente123`.

Colección de Postman: `backend/collection/La_Rotiseria.postman_collection.json`.

## Colaboradores

- Barzola Valentin
- Berardo Franco
- Boschin Lucas
- López García Francisco
- Sanz Martin

## Diseño (Figma)
- [Proyecto La Rotisería – URL](https://www.figma.com/design/sxQjjJiNuU7Bc7t37DVTBO/Proyecto-la-rotiseria?node-id=361-2286&t=9l1lSfHSqbpFrbbm-1)
