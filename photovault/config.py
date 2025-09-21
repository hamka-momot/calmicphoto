import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def get_engine_options(database_uri):
        """Get SQLAlchemy engine options based on database type"""
        # Optimize for serverless environments (Vercel)
        vercel_env = os.environ.get('VERCEL', '').lower() in ['true', '1', 'yes']
        if vercel_env:
            # Minimal pooling for serverless - each function instance is isolated
            from sqlalchemy.pool import NullPool
            base_options = {
                'pool_pre_ping': True,
                'pool_recycle': 30,     # Very short recycle for serverless
                'pool_timeout': 5,      # Fast timeout for serverless
                'poolclass': NullPool   # No connection pooling for serverless functions
            }
        else:
            # Standard pooling for traditional deployments
            base_options = {
                'pool_pre_ping': True,  # Validates connections before use
                'pool_recycle': 300,    # Recycle connections every 5 minutes
                'pool_timeout': 20,     # Timeout for connection checkout
                'pool_size': 5,         # Connection pool size
                'max_overflow': 10,     # Allow some overflow connections
            }
        
        if database_uri and 'postgresql' in database_uri:
            # PostgreSQL-specific settings
            base_options['connect_args'] = {
                'connect_timeout': 10,
                'sslmode': os.environ.get('DB_SSLMODE', 'require' if vercel_env else 'prefer'),  # Require SSL for Vercel
                'options': '-c statement_timeout=30s',
                'keepalives_idle': '600',
                'keepalives_interval': '30',
                'keepalives_count': '3'
            }
        
        return base_options
    
    # File upload settings
    # For autoscale deployment, use external storage or persistent volume
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Storage backend configuration
    USE_EXTERNAL_STORAGE = os.environ.get('USE_EXTERNAL_STORAGE', 'false').lower() == 'true'
    
    # External storage settings (for cloud object storage)
    STORAGE_PROVIDER = os.environ.get('STORAGE_PROVIDER', 's3')  # 's3' or 'gcs'
    STORAGE_BUCKET = os.environ.get('STORAGE_BUCKET')
    STORAGE_REGION = os.environ.get('STORAGE_REGION', 'us-east-1')
    STORAGE_ACCESS_KEY = os.environ.get('STORAGE_ACCESS_KEY')
    STORAGE_SECRET_KEY = os.environ.get('STORAGE_SECRET_KEY')
    STORAGE_ENDPOINT = os.environ.get('STORAGE_ENDPOINT')  # For S3-compatible services
    
    # Production storage requirements
    STORAGE_WARNING = """
    PRODUCTION STORAGE REQUIREMENT:
    - Default '/tmp/uploads' is EPHEMERAL and NOT suitable for autoscale deployment
    - Files will be LOST on container restarts and NOT shared across instances
    - For production, either:
      1. Set USE_EXTERNAL_STORAGE=true with cloud storage credentials
      2. Use single-instance deployment with persistent volume
      3. Configure UPLOAD_FOLDER to point to external mounted storage
    """
    
    # Camera-specific settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    CAMERA_QUALITY = 0.85  # JPEG quality for camera captures
    MAX_IMAGE_DIMENSION = 2048  # Maximum width/height for saved images
    
    # Session configuration - Railway compatible
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # HTTPS in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None  # Let Flask auto-detect for Railway
    
    # Security settings - Railway compatible
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = False  # Railway handles SSL termination
    WTF_CSRF_CHECK_DEFAULT = False  # Disable automatic CSRF for API routes
    
    # Mail settings (for user registration/password reset)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configuration"""
        # Create upload directory
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Log storage warning for autoscale deployments only if external storage is not configured
        if '/tmp/' in Config.UPLOAD_FOLDER and not Config.USE_EXTERNAL_STORAGE:
            app.logger.warning(Config.STORAGE_WARNING)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photovault_dev.db')
    
    # Development session settings - only apply if not in production mode
    if not os.environ.get('FLASK_CONFIG') == 'production':
        SESSION_COOKIE_SECURE = False  # Disable secure cookies for development
        WTF_CSRF_SSL_STRICT = False
        SESSION_COOKIE_SAMESITE = 'Lax'  # Replit proxy compatibility
        SESSION_COOKIE_DOMAIN = None  # Auto-detect domain for Replit
    
    def __init__(self):
        super().__init__()
        # Use custom engine options for development (no SSL requirement)
        database_uri = self.SQLALCHEMY_DATABASE_URI
        vercel_env = os.environ.get('VERCEL', '').lower() in ['true', '1', 'yes']
        if database_uri and 'postgresql' in database_uri:
            self.SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_pre_ping': True,
                'pool_recycle': 180,    # Shorter recycle time for development
                'pool_timeout': 30,     # Longer timeout for development
                'pool_size': 3,         # Smaller pool for development
                'max_overflow': 5,      # Smaller overflow for development
                'connect_args': {
                    'connect_timeout': 15,  # Longer connection timeout
                    'sslmode': 'require' if vercel_env else 'prefer',  # Require SSL for Vercel, prefer for Replit
                    'options': '-c statement_timeout=60s',  # Longer statement timeout
                    'keepalives_idle': '300',    # More aggressive keepalives
                    'keepalives_interval': '15', # More frequent keepalive checks
                    'keepalives_count': '5'      # More keepalive attempts
                }
            }
        else:
            self.SQLALCHEMY_ENGINE_OPTIONS = self.get_engine_options(database_uri)

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    def __init__(self):
        super().__init__()
        self.SQLALCHEMY_ENGINE_OPTIONS = self.get_engine_options(getattr(self, 'SQLALCHEMY_DATABASE_URI', None))
    
    # Production SECRET_KEY - generate random if not provided but log critical warning
    _secret_key = os.environ.get('SECRET_KEY') or os.environ.get('RAILWAY_SECRET_KEY')
    if not _secret_key:
        import secrets
        _secret_key = secrets.token_urlsafe(32)
        # This will be logged as a critical error in init_app
    SECRET_KEY = _secret_key
    
    # Force secure session settings for production (Railway, Replit, etc.)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True  
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    WTF_CSRF_SSL_STRICT = False  # Proxy handles SSL termination
    WTF_CSRF_TIME_LIMIT = None
    
    # Handle Railway's DATABASE_URL format (postgresql:// vs postgres://)
    # Railway may use different variable names at different phases
    database_url = (os.environ.get('DATABASE_URL') or 
                   os.environ.get('RAILWAY_DATABASE_URL') or
                   os.environ.get('DATABASE_PRIVATE_URL') or
                   os.environ.get('DATABASE_PUBLIC_URL'))
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Require explicit confirmation for SQLite in production
    if not database_url:
        if os.environ.get('ALLOW_SQLITE_IN_PROD') == '1':
            database_url = 'sqlite:///photovault_production.db'
        else:
            # Set to None to trigger fail-fast in init_app
            database_url = None
    
    SQLALCHEMY_DATABASE_URI = database_url
    
    
    # Production logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', '1')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Critical security checks
        if not (os.environ.get('SECRET_KEY') or os.environ.get('RAILWAY_SECRET_KEY')):
            app.logger.critical('SECURITY RISK: SECRET_KEY not provided! Generated random key for this session only. '
                              'Set SECRET_KEY environment variable immediately! User sessions will not persist across restarts.')
        
        # Log deployment environment detection for debugging
        railway_detected = any([
            os.environ.get('RAILWAY_ENVIRONMENT_NAME'),
            os.environ.get('RAILWAY_SERVICE_NAME'),
            os.environ.get('RAILWAY_PROJECT_ID'),
            os.environ.get('RAILWAY_DEPLOYMENT_ID'),
            os.environ.get('NIXPACKS_METADATA'),
            'railway' in os.environ.get('HOSTNAME', '').lower(),
            'railway' in os.environ.get('RAILWAY_PUBLIC_DOMAIN', '').lower()
        ])
        
        replit_detected = any([
            os.environ.get('REPLIT'),
            os.environ.get('REPL_ID'),
            'replit' in os.environ.get('HOSTNAME', '').lower()
        ])
        
        if railway_detected:
            app.logger.info('Railway deployment detected - using ProxyFix with secure session settings')
        elif replit_detected:
            app.logger.info('Replit deployment detected - using ProxyFix with secure session settings')
        else:
            app.logger.info('Standard deployment detected - using secure session settings')
            
        app.logger.info(f'Session cookie secure: {app.config.get("SESSION_COOKIE_SECURE", "Not set")}')
        app.logger.info(f'Preferred URL scheme: {app.config.get("PREFERRED_URL_SCHEME", "Not set")}')
        
        # Check for database configuration with Railway-specific handling
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            # Detect Railway environment through multiple indicators
            railway_indicators = [
                os.environ.get('RAILWAY_ENVIRONMENT_NAME'),
                os.environ.get('RAILWAY_SERVICE_NAME'),
                os.environ.get('RAILWAY_PROJECT_ID'),
                os.environ.get('RAILWAY_DEPLOYMENT_ID'),
                os.environ.get('NIXPACKS_METADATA')  # Railway uses Nixpacks
            ]
            
            if any(railway_indicators):
                # We're in Railway - use SQLite as fallback and continue startup
                # Railway will eventually provide DATABASE_URL and app can reconnect
                app.logger.warning('Railway deployment detected. DATABASE_URL timing issue - using SQLite fallback for startup.')
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp_railway_fallback.db'
                
                # Set flag to attempt database reconnection later
                app.config['RAILWAY_FALLBACK_MODE'] = True
            else:
                # Not Railway, enforce strict validation
                app.logger.critical('DATABASE_URL environment variable must be set for production. '
                                  'Set DATABASE_URL or ALLOW_SQLITE_IN_PROD=1 to use SQLite (data loss risk).')
                raise RuntimeError('DATABASE_URL environment variable must be set for production')
        
        if 'sqlite' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            app.logger.warning('SQLite enabled in production via ALLOW_SQLITE_IN_PROD=1 - data may be lost on restarts')
        
        # Log configuration for debugging (without exposing credentials)
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        if db_uri != 'Not set':
            if 'sqlite' in db_uri:
                app.logger.info("Database: SQLite")
            elif 'postgresql' in db_uri:
                # Log SSL mode for production security verification
                engine_options = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
                connect_args = engine_options.get('connect_args', {})
                ssl_mode = connect_args.get('sslmode', 'unknown')
                app.logger.info(f"Database: PostgreSQL (SSL mode: {ssl_mode})")
            else:
                app.logger.info("Database: Configured")
        else:
            app.logger.info("Database: Not set")
        
        # Configure logging for production
        import logging
        import sys
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            # Use stdout/stderr logging for containerized environments (Replit Autoscale)
            if os.environ.get('LOG_TO_STDOUT', '').lower() in ['true', '1', 'yes']:
                stream_handler = logging.StreamHandler(sys.stdout)
                stream_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                ))
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            else:
                # Default to stdout for production deployments like Replit Autoscale
                stream_handler = logging.StreamHandler(sys.stdout)
                stream_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                ))
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('PhotoVault startup')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}