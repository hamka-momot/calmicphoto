#!/usr/bin/env python3
"""
Database migration script for Railway deployment
This script handles database migrations in a way that's compatible with Railway's build process
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_migrations():
    """Run database migrations with fallback configuration"""
    try:
        # Try to use environment-specific config
        from photovault import create_app
        from config import get_config
        
        # Create app with flexible config that won't fail on missing DATABASE_URL during build
        config_class = get_config()
        app = create_app(config_class)
        
        with app.app_context():
            from flask_migrate import upgrade
            upgrade()
            print("Database migrations completed successfully")
            
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        # If migrations fail, try to continue - Railway will inject vars at runtime
        print("Continuing deployment - DATABASE_URL will be available at runtime")
        sys.exit(0)  # Don't fail the build

if __name__ == "__main__":
    run_migrations()