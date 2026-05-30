"""
Configuration management for AI Meeting Rescue Agent
Handles environment variables and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # IBM watsonx.ai Configuration
    WATSONX_API_KEY = os.getenv('WATSONX_API_KEY')
    WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
    WATSONX_URL = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
    
    # Granite LLM Configuration
    GRANITE_MODEL_ID = os.getenv('GRANITE_MODEL_ID', 'ibm/granite-13b-chat-v2')
    GRANITE_MAX_TOKENS = int(os.getenv('GRANITE_MAX_TOKENS', 2000))
    GRANITE_TEMPERATURE = float(os.getenv('GRANITE_TEMPERATURE', 0.7))
    GRANITE_TOP_P = float(os.getenv('GRANITE_TOP_P', 1.0))
    GRANITE_TOP_K = int(os.getenv('GRANITE_TOP_K', 50))
    
    # Processing Configuration
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 5))
    TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', 300))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        required_vars = [
            'WATSONX_API_KEY',
            'WATSONX_PROJECT_ID'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        return True


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Made with Bob
