# photovault/utils/storage_service.py

import os
import logging
from flask import current_app

logger = logging.getLogger(__name__)

# S3 Storage Service
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class StorageService:
    """Unified storage service supporting local and S3 storage"""
    
    def __init__(self, app=None):
        self.app = app
        self.s3_client = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize storage service with Flask app"""
        self.app = app
        if app.config.get('USE_EXTERNAL_STORAGE', False):
            self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize S3 client for external storage"""
        if not BOTO3_AVAILABLE:
            logger.error("boto3 is required for external storage but not available")
            return
            
        try:
            config = current_app.config
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.get('STORAGE_ACCESS_KEY'),
                aws_secret_access_key=config.get('STORAGE_SECRET_KEY'),
                region_name=config.get('STORAGE_REGION', 'us-east-1'),
                endpoint_url=config.get('STORAGE_ENDPOINT')
            )
            logger.info("S3 client initialized for external storage")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None
    
    def save_file(self, file_obj, key, user_id=None):
        """
        Save file to storage (local or S3)
        
        Args:
            file_obj: File object to save
            key: Storage key/filename
            user_id: Optional user ID for organization
            
        Returns:
            tuple: (success, file_path_or_url_or_error)
        """
        config = current_app.config
        use_external = config.get('USE_EXTERNAL_STORAGE', False)
        
        if use_external:
            return self._save_to_s3(file_obj, key, user_id)
        else:
            return self._save_to_local(file_obj, key, user_id)
    
    def _save_to_s3(self, file_obj, key, user_id=None):
        """Save file to S3 storage"""
        try:
            if not self.s3_client:
                self._init_s3_client()
                
            if not self.s3_client:
                return False, "S3 client not available"
            
            config = current_app.config
            bucket = config.get('STORAGE_BUCKET')
            if not bucket:
                return False, "Storage bucket not configured"
            
            # Create S3 key with user organization
            s3_key = f"{user_id}/{key}" if user_id else key
            
            # Reset file pointer and get content type
            file_obj.seek(0)
            content_type = getattr(file_obj, 'content_type', 'application/octet-stream')
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=file_obj.read(),
                ContentType=content_type,
                ServerSideEncryption='AES256'
            )
            
            # Generate public URL
            url = self._generate_s3_url(bucket, s3_key)
            logger.info(f"File uploaded to S3: {s3_key}")
            return True, url
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"S3 upload error: {str(e)}")
            return False, f"S3 upload failed: {str(e)}"
        except Exception as e:
            logger.error(f"External storage error: {str(e)}")
            return False, f"Storage error: {str(e)}"
    
    def _save_to_local(self, file_obj, key, user_id=None):
        """Save file to local filesystem"""
        try:
            config = current_app.config
            upload_folder = config.get('UPLOAD_FOLDER', 'uploads')
            
            if user_id:
                upload_folder = os.path.join(upload_folder, str(user_id))
            
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, key)
            file_obj.save(file_path)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                logger.info(f"File saved locally: {key}")
                return True, file_path
            else:
                return False, "File save verification failed"
                
        except Exception as e:
            logger.error(f"Local storage error: {str(e)}")
            return False, f"Local storage error: {str(e)}"
    
    def _generate_s3_url(self, bucket, key):
        """Generate S3 URL for file"""
        config = current_app.config
        region = config.get('STORAGE_REGION', 'us-east-1')
        endpoint = config.get('STORAGE_ENDPOINT')
        
        if endpoint:
            # Custom endpoint (DigitalOcean Spaces, MinIO, etc.)
            if endpoint.endswith('/'):
                endpoint = endpoint[:-1]
            return f"{endpoint}/{bucket}/{key}"
        else:
            # Standard AWS S3
            return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    
    def delete_file(self, path_or_key, user_id=None):
        """Delete file from storage"""
        config = current_app.config
        use_external = config.get('USE_EXTERNAL_STORAGE', False)
        
        if use_external:
            return self._delete_from_s3(path_or_key, user_id)
        else:
            return self._delete_from_local(path_or_key)
    
    def _delete_from_s3(self, key, user_id=None):
        """Delete file from S3"""
        try:
            if not self.s3_client:
                return False, "S3 client not available"
                
            bucket = current_app.config.get('STORAGE_BUCKET')
            s3_key = f"{user_id}/{key}" if user_id else key
            
            self.s3_client.delete_object(Bucket=bucket, Key=s3_key)
            logger.info(f"File deleted from S3: {s3_key}")
            return True, "File deleted successfully"
            
        except Exception as e:
            logger.error(f"S3 delete error: {str(e)}")
            return False, f"Delete error: {str(e)}"
    
    def _delete_from_local(self, file_path):
        """Delete file from local filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted locally: {file_path}")
                return True, "File deleted successfully"
            else:
                return False, "File not found"
        except Exception as e:
            logger.error(f"Local delete error: {str(e)}")
            return False, f"Delete error: {str(e)}"
    
    def file_exists(self, path_or_key, user_id=None):
        """Check if file exists in storage"""
        config = current_app.config
        use_external = config.get('USE_EXTERNAL_STORAGE', False)
        
        if use_external:
            return self._exists_in_s3(path_or_key, user_id)
        else:
            return self._exists_locally(path_or_key)
    
    def _exists_in_s3(self, key, user_id=None):
        """Check if file exists in S3"""
        try:
            if not self.s3_client:
                return False
                
            bucket = current_app.config.get('STORAGE_BUCKET')
            s3_key = f"{user_id}/{key}" if user_id else key
            
            self.s3_client.head_object(Bucket=bucket, Key=s3_key)
            return True
        except ClientError:
            return False
        except Exception:
            return False
    
    def _exists_locally(self, file_path):
        """Check if file exists locally"""
        return os.path.exists(file_path)

# Global storage service instance
storage_service = StorageService()