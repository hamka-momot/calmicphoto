"""
PhotoVault Vercel Serverless Entry Point
This file serves as the entry point for Vercel serverless deployment
"""
import sys
import os
from flask import Flask

# Add the root directory to Python path so we can import photovault
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    # Load environment variables if dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not available in serverless environment
    
    # Set Vercel-specific environment variables for serverless
    os.environ.setdefault('FLASK_CONFIG', 'production')
    os.environ.setdefault('VERCEL', 'true')
    
    # Enforce external storage for Vercel serverless deployment
    if not os.environ.get('USE_EXTERNAL_STORAGE', '').lower() in ['true', '1', 'yes']:
        missing_vars = []
        required_storage_vars = ['STORAGE_BUCKET', 'STORAGE_ACCESS_KEY', 'STORAGE_SECRET_KEY']
        for var in required_storage_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise RuntimeError(
                f"CRITICAL: External storage required for Vercel deployment. "
                f"Missing environment variables: {', '.join(missing_vars)}. "
                f"Set USE_EXTERNAL_STORAGE=true and configure all storage credentials."
            )
    
    # Auto-enable external storage if bucket is configured
    if os.environ.get('STORAGE_BUCKET'):
        os.environ.setdefault('USE_EXTERNAL_STORAGE', 'true')
    
    from photovault import create_app
    from config import get_config
    
    # Create the Flask app for Vercel serverless deployment
    app = create_app(get_config())
    
    # Disable Flask development server warnings
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
except Exception as e:
    # Fallback in case of import issues
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"PhotoVault Import Error: {str(e)}. Please check environment configuration.", 500
    
    @app.route('/health')
    def health():
        return {"status": "error", "message": "Configuration issue"}, 500

# This is the WSGI application object that Vercel will use
application = app

# For development testing only (not used in Vercel)
if __name__ == '__main__':
    # This won't run in Vercel serverless environment
    app.run(debug=False, host='0.0.0.0', port=5000)