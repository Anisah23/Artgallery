import os
from typing import Optional


class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///artgallery.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))  # 24 hours
    
    # Cloudinary Configuration
    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "cloudinary://614532782658179:hN1dlBjrkD1NdANF2eWYyQmMueg@ddby7bbdg")
    
    # Parse Cloudinary URL
    if CLOUDINARY_URL:
        import urllib.parse
        parsed = urllib.parse.urlparse(CLOUDINARY_URL)
        CLOUDINARY_CLOUD_NAME = parsed.hostname
        CLOUDINARY_API_KEY = parsed.username
        CLOUDINARY_API_SECRET = parsed.password
    else:
        CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
        CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
        CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    
    # Postmark Configuration
    POSTMARK_API_TOKEN = os.getenv("POSTMARK_API_TOKEN", "35d30282-b672-47b0-aa50-109d97b65f2c")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@artmarket.com")
    
    # Stripe Configuration
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:artowner@localhost:5432/artgallery_test")


def get_config() -> Config:
    config_name = os.getenv("FLASK_ENV", "development")
    config_mapping = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    return config_mapping.get(config_name, DevelopmentConfig)()