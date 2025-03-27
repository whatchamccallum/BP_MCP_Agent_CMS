"""
Configuration module for the CMS.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('dev.env')

class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-do-not-use-in-production')
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Storage settings
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')
    STORAGE_BASE_DIR = os.getenv('STORAGE_BASE_DIR', os.path.join(os.getcwd(), 'storage_files'))
    STORAGE_S3_BUCKET = os.getenv('STORAGE_S3_BUCKET', 'bp-mcp-agent-cms')
    STORAGE_S3_ACCESS_KEY = os.getenv('STORAGE_S3_ACCESS_KEY')
    STORAGE_S3_SECRET_KEY = os.getenv('STORAGE_S3_SECRET_KEY')
    STORAGE_S3_REGION = os.getenv('STORAGE_S3_REGION')
    STORAGE_S3_ENDPOINT = os.getenv('STORAGE_S3_ENDPOINT')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
    UPLOAD_EXTENSIONS = {
        'video': ['.mp4', '.avi', '.mov', '.webm'],
        'image': ['.jpg', '.jpeg', '.png', '.gif'],
        'report': ['.html', '.pdf', '.csv']
    }
    
    # Breaking Point MCP Agent settings
    BP_MCP_AGENT_HOST = os.getenv('BP_MCP_AGENT_HOST', 'localhost')
    BP_MCP_AGENT_PORT = os.getenv('BP_MCP_AGENT_PORT', '5000')
    BP_MCP_AGENT_USERNAME = os.getenv('BP_MCP_AGENT_USERNAME', 'admin')
    BP_MCP_AGENT_PASSWORD = os.getenv('BP_MCP_AGENT_PASSWORD', 'admin')


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI', 'sqlite:///bp_mcp_agent_cms_dev.db')


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'sqlite:///bp_mcp_agent_cms_test.db')


class ProductionConfig(Config):
    """Production configuration."""
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///bp_mcp_agent_cms.db')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
