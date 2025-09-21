# PhotoVault Vercel Deployment Guide

## Overview
This guide walks you through deploying PhotoVault on Vercel's serverless platform with external storage and PostgreSQL database.

## Prerequisites
- Vercel account
- PostgreSQL database (Neon, Supabase, or AWS RDS)
- S3-compatible storage (AWS S3, DigitalOcean Spaces, or Cloudflare R2)

## Step 1: Fork and Import to Vercel

1. Fork the PhotoVault repository to your GitHub account
2. In Vercel dashboard, click "New Project"
3. Import your forked repository
4. Vercel will auto-detect it as a Python project

## Step 2: Environment Variables Configuration

In your Vercel project settings → Environment Variables, add the following:

### Required Database Configuration
```
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
```

### Required Storage Configuration (S3-Compatible)
```
USE_EXTERNAL_STORAGE=true
STORAGE_BUCKET=your-bucket-name
STORAGE_REGION=us-east-1
STORAGE_ACCESS_KEY=your-s3-access-key
STORAGE_SECRET_KEY=your-s3-secret-key
```

### Optional Storage Configuration
```
STORAGE_ENDPOINT=https://your-custom-endpoint.com
```
*Only needed for non-AWS S3 providers like DigitalOcean Spaces, Cloudflare R2, etc.*

### Optional Email Configuration (Replit Mail)
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Step 3: Database Setup

### Using Neon (Recommended)
1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string
4. Add it to Vercel as `DATABASE_URL`

### Using Supabase
1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string (Transaction pooler)
5. Add it to Vercel as `DATABASE_URL`

### Database Migration
Since Vercel is serverless, you need to run migrations separately:

```bash
# Local setup for migrations
git clone your-forked-repo
cd photovault
pip install -r requirements.txt
export DATABASE_URL="your-production-database-url"
flask db upgrade
```

## Step 4: Storage Setup

### Using AWS S3
1. Create an S3 bucket
2. Create an IAM user with S3 access
3. Set bucket policy for public read access (for photo serving):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

### Using DigitalOcean Spaces
1. Create a Space in DigitalOcean
2. Generate API keys (Spaces access keys)
3. Use your Space's endpoint URL as `STORAGE_ENDPOINT`

### Using Cloudflare R2
1. Create an R2 bucket
2. Generate API tokens with R2 permissions
3. Use R2's S3-compatible endpoint as `STORAGE_ENDPOINT`

## Step 5: Deploy to Vercel

1. Push your changes to GitHub (if any)
2. Vercel will automatically deploy
3. Check the deployment logs for any errors
4. Visit your deployed URL to test the application

## Step 6: Testing Your Deployment

1. **Registration Test**: Create a new user account
2. **Photo Upload Test**: Upload a photo and verify it appears
3. **Storage Test**: Check that photos are saved to your S3 bucket
4. **Database Test**: Log out and log back in to verify database connectivity

## Important Notes

### Function Limitations
- Vercel functions have a 60-second timeout (configured in vercel.json)
- Large image processing operations might timeout
- **⚠️ OpenCV/NumPy dependencies may exceed Vercel size limits**
- Consider creating a lightweight version without image enhancement for Vercel

### Cold Start Performance
- First request might be slower due to cold start
- Heavy dependencies (OpenCV, NumPy) increase cold start time
- **For production:** Consider removing OpenCV features or using external processing service

### Current Limitations
- **Thumbnail generation:** Currently works with local files only; needs S3 integration
- **Heavy dependencies:** Full OpenCV package may exceed Vercel bundle size limits
- **Image enhancement:** May need to be disabled or moved to external service for Vercel

### File Storage
- Photos are stored in your S3-compatible storage
- Temporary files use `/tmp` which is cleared between invocations
- Never store permanent data in local filesystem on serverless

## Troubleshooting

### Deployment Fails
- Check Vercel build logs for Python dependency errors
- Ensure `requirements.txt` has all necessary packages
- Verify Python version compatibility

### Database Connection Issues
- Verify `DATABASE_URL` format includes `sslmode=require`
- Check database connection limits
- Ensure database accepts connections from Vercel IPs

### Photo Upload/Display Issues
- Verify S3 bucket permissions
- Check `STORAGE_ACCESS_KEY` and `STORAGE_SECRET_KEY`
- Ensure bucket policy allows public read access

### Function Timeouts
- Monitor function execution time in Vercel dashboard
- Consider reducing image processing complexity
- Implement background processing for heavy operations

## Security Recommendations

1. **Environment Variables**: Never commit secrets to code
2. **S3 Security**: Use least-privilege IAM policies
3. **Database**: Use connection pooling and SSL
4. **HTTPS**: Vercel provides HTTPS by default
5. **CORS**: Configure CORS if needed for API access

## Performance Optimization

1. **Database**: Use connection pooling (configured automatically)
2. **Storage**: Use CDN for frequently accessed images
3. **Caching**: Implement Redis caching for sessions if needed
4. **Images**: Consider image optimization before upload

## Cost Considerations

- **Vercel**: Free tier includes 100GB bandwidth, 1000 function hours
- **Storage**: S3 costs depend on storage and bandwidth usage
- **Database**: Neon free tier includes 512MB storage
- **Monitor**: Track usage in respective dashboards

Your PhotoVault application should now be successfully running on Vercel with external storage and database!