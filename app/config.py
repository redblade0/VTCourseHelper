"""
Configuration Management
Handles all environment-based configuration
"""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration with defaults"""
    
    # Flask
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Cache
    CACHE_EXPIRY = timedelta(days=int(os.getenv('CACHE_EXPIRY_DAYS', 7)))
    
    # Scrapers
    RMP_TIMEOUT = int(os.getenv('RMP_TIMEOUT', 10))
    REDDIT_TIMEOUT = int(os.getenv('REDDIT_TIMEOUT', 10))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://vt_user:vt_password@localhost:5432/vt_coursehelper'
    )
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    EXPLAIN_TEMPLATE_LOADING = True


class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration mapping
CONFIG = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}


def get_config(env: str = None) -> BaseConfig:
    """
    Get configuration object based on environment
    
    Args:
        env: Environment name (development, testing, production)
    
    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return CONFIG.get(env, DevelopmentConfig)