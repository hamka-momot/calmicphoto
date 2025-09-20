# PhotoVault Deployment Guide

## Render Ready Configuration

PhotoVault is configured for autoscale deployment with the following requirements:

### Required Environment Variables

#### Essential Configuration
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Cryptographic secret for sessions (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `FLASK_CONFIG=production` - Enables production configuration

#### Storage Configuration (Critical for Autoscale)
Choose one of the following storage options:

**Option 1: External Object Storage (Recommended)**
```
USE_EXTERNAL_STORAGE=true
STORAGE_BUCKET=your-bucket-name
STORAGE_ACCESS_KEY=your-access-key
STORAGE_SECRET_KEY=your-secret-key
STORAGE_ENDPOINT=https://s3.amazonaws.com  # Optional for non-AWS S3-compatible services
STORAGE_REGION=us-east-1
```

**Option 2: Persistent Volume (Single Instance)**
```
UPLOAD_FOLDER=/persistent/uploads
```

**Option 3: Development/Testing Only (Files will be lost)**
```
# No additional configuration - uses ephemeral /tmp/uploads
```

#### Optional Configuration
- `LOG_TO_STDOUT=1` - Enable container-friendly logging
- `HTTPS=true` - Enable secure cookie settings

### Deployment Types

#### Autoscale Deployment (Recommended)
- **Best for**: Variable traffic, high availability
- **Requirements**: External storage or single instance with persistent volume
- **Configuration**: Uses `wsgi:app` with Gunicorn

#### VM Deployment
- **Best for**: Persistent workloads, local file storage
- **Requirements**: Persistent disk storage
- **Configuration**: Can use local file storage

### Pre-deployment Checklist

1. ✅ Database configured (PostgreSQL recommended)
2. ✅ SECRET_KEY set to persistent value
3. ✅ Storage solution configured (external storage for autoscale)
4. ✅ Environment variables set
5. ✅ Database migrations ready

### Post-deployment

1. Run database migrations: `alembic upgrade head`
2. Verify storage functionality by uploading a test image
3. Check application logs for any storage warnings

### Troubleshooting

#### Storage Warnings
If you see storage warnings in logs, configure external storage or use single-instance deployment.

#### Database Connection Issues
Ensure DATABASE_URL is properly formatted: `postgresql://user:password@host:port/database`

#### Session Issues
Ensure SECRET_KEY is set and persistent across deployments.