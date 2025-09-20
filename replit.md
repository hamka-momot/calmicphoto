# Overview

PhotoVault is a professional photo management platform by Calmic Sdn Bhd, focusing on secure storage, advanced editing, and comprehensive organization of photographs. Leveraging Flask, it provides enterprise-grade security, role-based access control, and robust features for managing photo collections, including user management and administrative tools. The platform's goal is to offer a secure and efficient solution for personal and professional photo archiving with business vision, market potential, and project ambitions.

# Recent Changes

## September 20, 2025 - Fresh Replit Environment Import & Complete Setup
- **Fresh GitHub Import**: Successfully imported PhotoVault repository from GitHub to clean Replit environment
- **Python Environment**: Installed Python 3.11 with all required dependencies from requirements.txt (Flask, SQLAlchemy, image processing libraries)
- **Database Setup**: Created and configured PostgreSQL database with proper environment variables (DATABASE_URL, PGHOST, etc.)
- **Schema Fixes**: Resolved database schema mismatch by creating proper Alembic migration for missing User table columns (is_active, updated_at)
- **Model Alignment**: Updated User model to include is_active field, ensuring database and ORM alignment
- **Development Server**: Configured Flask application to run on port 5000 with 0.0.0.0 host binding for Replit proxy compatibility
- **Production Deployment**: Set up autoscale deployment configuration using Gunicorn with wsgi:app endpoint
- **Frontend Verification**: Confirmed PhotoVault website loads correctly with Bootstrap 5 styling and Calmic branding, registration functionality works
- **OpenCV Integration**: Verified image enhancement features are working with OpenCV-headless
- **Migration System**: Verified all Alembic migrations work correctly for fresh deployments
- All core systems operational: web server, database connectivity, static file serving, user registration/authentication, and application routing

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend
-   **Framework**: Flask for core web application, routing, and request handling.
-   **Database ORM**: Flask-SQLAlchemy for database interactions.
-   **Authentication**: Flask-Login for user session management, with Werkzeug for password hashing.
-   **Database Migrations**: Flask-Migrate for schema management using Alembic.
-   **Form Handling & Security**: Flask-WTF for form processing and CSRF protection.
-   **Security**: Role-Based Access Control (User, Admin, Superuser), server-side input validation, file validation, and decorator-based route protection.
-   **File Management**: Pillow for image manipulation, Werkzeug for secure filename handling, and organized storage for original and edited versions.
-   **API**: `/api` health check endpoint for monitoring.

## Frontend
-   **Templating**: Jinja2 with Bootstrap 5 for a responsive and modern UI.
-   **Photo Editing**: Client-side canvas-based editing with JavaScript, including responsive sizing and coordinate mapping for various devices.
-   **Camera Integration**: WebRTC getUserMedia API for direct camera access with dual-mode (Sequential and Quad Split) photo capture.
-   **Design**: Mobile-responsive with touch support, professional Calmic branding, and updated navigation bar with a darker theme.

## Photo Management Features
-   **Storage**: Maintains separate original and edited versions of photos.
-   **Metadata**: Tracks file size, upload timestamps, and editing history.
-   **Organization**: Supports album creation (time-based, event-based) and person tagging.
-   **Enhancement**: OpenCV-based advanced image processing for old photograph restoration (CLAHE, bilateral filtering, auto-levels, brightness/contrast adjustments).

# External Dependencies

## Core Framework
-   **Flask**: Web application framework.
-   **Flask-SQLAlchemy**: Database ORM.
-   **Flask-Login**: User authentication.
-   **Flask-Migrate**: Database migrations.
-   **Flask-WTF**: Form handling and CSRF protection.

## Database
-   **PostgreSQL**: Primary database for the Replit environment (configured with native Replit PostgreSQL integration).
-   **SQLAlchemy**: Database abstraction layer.
-   **Flask-Migrate**: Database migration management with Alembic.

## Image Processing
-   **Pillow**: Image manipulation and validation.
-   **Canvas API**: Client-side image editing.
-   **OpenCV.js**: Advanced computer vision and photo enhancement.
-   **scikit-image**: Image processing library.

## Frontend Libraries
-   **Bootstrap 5**: CSS framework for responsive design.
-   **Bootstrap Icons**: Icon library.
-   **WebRTC getUserMedia**: For camera access.

## Production & Development Utilities
-   **Gunicorn**: WSGI HTTP server for production.
-   **python-dotenv**: Environment variable management.
-   **Werkzeug**: WSGI utilities and security.