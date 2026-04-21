import boto3
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class S3VideoManager:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def upload_video(self, file_obj, lesson_id, course_id):
        """Upload video to S3"""
        try:
            key = f'videos/courses/{course_id}/lessons/{lesson_id}/{file_obj.name}'
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': file_obj.content_type,
                    'ACL': 'private'
                }
            )
            
            # Generate signed URL (valid for 7 days)
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=7*24*60*60  # 7 days
            )
            
            logger.info(f"Video uploaded: {key}")
            return {
                'url': signed_url,
                'key': key,
                'size': file_obj.size
            }
        
        except Exception as e:
            logger.error(f"Video upload error: {str(e)}")
            raise
    
    def delete_video(self, s3_key):
        """Delete video from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Video deleted: {s3_key}")
        except Exception as e:
            logger.error(f"Video deletion error: {str(e)}")
    
    def get_signed_url(self, s3_key, expiration=7*24*60*60):
        """Get signed URL for video"""
        try:
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return signed_url
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {str(e)}")
            raise
