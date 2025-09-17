# Flask only loads these for the development server, not for production runs
FLASK_APP=src.app:create_app()
SECRET_KEY=super-secret-key
SQLITE_PATH=./dev.db