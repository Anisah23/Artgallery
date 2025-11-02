import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app
import secrets
from PIL import Image
import io
import os


class CloudinaryService:
    @staticmethod
    def configure_cloudinary():
        """Configure Cloudinary with environment variables"""
        cloudinary.config(
            cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
            api_key=current_app.config.get('CLOUDINARY_API_KEY'),
            api_secret=current_app.config.get('CLOUDINARY_API_SECRET'),
            secure=True
        )

    @staticmethod
    def optimize_image(image_file, max_size=(1200, 1200), quality=85):
        """Optimize image before upload"""
        try:
            # Open image
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            return output
        except Exception as e:
            current_app.logger.error(f"Image optimization failed: {str(e)}")
            # Return original file if optimization fails
            image_file.seek(0)
            return image_file

    @staticmethod
    def upload_image(image_file, folder="artworks"):
        """Upload image to Cloudinary with optimization"""
        try:
            CloudinaryService.configure_cloudinary()
            
            # Generate unique public ID
            public_id = f"{folder}/{secrets.token_urlsafe(16)}"
            
            # Optimize image
            optimized_image = CloudinaryService.optimize_image(image_file)
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                optimized_image,
                public_id=public_id,
                folder=folder,
                transformation=[
                    {"width": 1200, "height": 1200, "crop": "limit"},
                    {"quality": "auto:good"},
                    {"format": "jpg"}
                ]
            )
            
            return {
                "public_id": upload_result["public_id"],
                "url": upload_result["secure_url"],
                "format": upload_result["format"],
                "width": upload_result["width"],
                "height": upload_result["height"]
            }
        except Exception as e:
            current_app.logger.error(f"Cloudinary upload failed: {str(e)}")
            raise Exception("Image upload failed")

    @staticmethod
    def delete_image(public_id):
        """Delete image from Cloudinary"""
        try:
            CloudinaryService.configure_cloudinary()
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            current_app.logger.error(f"Cloudinary delete failed: {str(e)}")
            return False