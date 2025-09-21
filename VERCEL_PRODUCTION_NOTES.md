# Vercel Production Deployment Notes

## ⚠️ Critical Bundle Size Warning

The current PhotoVault application includes heavy image processing dependencies that may cause deployment issues on Vercel:

### Problematic Dependencies
- `opencv-python-headless` (~50MB)
- `scikit-image` (~15MB) 
- `numpy` (~20MB)
- Total bundle size may exceed Vercel's 250MB limit

### Production Solutions

#### Option 1: Lightweight Deployment (Recommended for Vercel)
Create a separate `requirements-vercel.txt` without heavy dependencies:

```txt
# Core Flask dependencies only
Flask==3.0.3
Werkzeug==3.0.3
Flask-Login==0.6.3
Flask-Migrate==4.1.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
SQLAlchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
Pillow==11.0.0
WTForms==3.1.1
email-validator==2.1.0
python-dotenv==1.0.0
python-decouple==3.8
click==8.1.7
itsdangerous==2.2.0
Jinja2==3.1.4
MarkupSafe==2.1.5
blinker==1.7.0
exifread==3.5.1
requests==2.31.0
boto3==1.29.7
gunicorn==21.2.0
```

#### Option 2: Feature Flags
Add environment variable to disable heavy image processing:
```
DISABLE_IMAGE_ENHANCEMENT=true
```

#### Option 3: External Processing Service
Move image enhancement to external service (AWS Lambda, dedicated server, etc.)

## Configuration Changes Made

### 1. Storage Enforcement
- External storage is now **required** for Vercel deployment
- Application will fail fast if storage credentials are missing
- Prevents data loss in serverless environment

### 2. Database Optimization  
- SSL mode set to "require" for Vercel (vs "prefer" for Replit)
- NullPool for serverless database connections
- Shorter connection recycling for function lifecycles

### 3. Performance Optimizations
- Static assets excluded from Flask function routing
- Memory increased to 1024MB for image processing
- Timeout set to 60 seconds maximum

### 4. Environment Detection
- Robust VERCEL environment variable parsing
- Automatic configuration switching between development and production

## Deployment Checklist

Before deploying to Vercel:

- [ ] Configure external storage (S3, R2, Spaces)
- [ ] Set up PostgreSQL database (Neon, Supabase, etc.)
- [ ] Set required environment variables
- [ ] Consider using lightweight requirements.txt
- [ ] Test bundle size doesn't exceed limits
- [ ] Run database migrations externally
- [ ] Verify image upload/display works end-to-end

## Environment Variables Required for Vercel

```
DATABASE_URL=postgresql://...?sslmode=require
SECRET_KEY=your-secret-key
USE_EXTERNAL_STORAGE=true
STORAGE_BUCKET=your-bucket-name
STORAGE_ACCESS_KEY=your-access-key
STORAGE_SECRET_KEY=your-secret-key
STORAGE_REGION=us-east-1
VERCEL=true
```

## Known Limitations

- Large image processing may timeout (60s limit)
- Cold starts will be slower with heavy dependencies
- Image enhancement features may need to be disabled or moved external
- All file storage must be external (no local filesystem persistence)