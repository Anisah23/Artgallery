from flask import Flask
from flask_cors import CORS
from .config import get_config
from .extensions import db, migrate, jwt, ma
from .swagger import swagger_bp, api

def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or get_config())

    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # Disable strict slashes to prevent 308 redirects on preflight
    app.url_map.strict_slashes = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    # Register blueprints
    app.register_blueprint(swagger_bp, url_prefix='/api')

    # Configure JWT
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, str):
            return user
        return str(user.id)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from .models.user import User
        identity = jwt_data["sub"]
        try:
            return User.query.filter_by(id=identity).one_or_none()
        except Exception:
            return None

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'ArtMarket API'}

    # Database connection check endpoint
    @app.route('/db-check')
    def db_check():
        try:
            from .extensions import db
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            return {'status': 'connected', 'database': 'PostgreSQL'}
        except Exception as e:
            return {'status': 'disconnected', 'error': str(e)}, 500

    return app