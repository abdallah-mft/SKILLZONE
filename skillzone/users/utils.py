import os
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def handle_avatar_upload(image_file, user_id):
    """Process and save avatar image with validation and optimization"""
    try:
        # Open image using PIL
        img = Image.open(image_file)
        
        # Validate file type
        allowed_types = {'PNG', 'JPEG', 'JPG'}
        if img.format not in allowed_types:
            raise ValueError("Invalid image format. Allowed formats: PNG, JPEG, JPG")
            
        # Validate file size (max 5MB)
        if image_file.size > 5 * 1024 * 1024:
            raise ValueError("Image size too large. Maximum size: 5MB")
            
        # Resize image while maintaining aspect ratio
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Generate unique filename
        filename = f"avatar_{user_id}_{os.urandom(8).hex()}.jpg"
        path = os.path.join('avatars', filename)
        
        # Save optimized image
        output = ContentFile(b'')
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Save using Django's storage system
        path = default_storage.save(path, output)
        
        return path
        
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

def send_verification_email(user, verification_url):
    """Send HTML email verification"""
    context = {
        'user': user,
        'verification_url': verification_url,
        'expiry_days': settings.EMAIL_VERIFICATION_TIMEOUT_DAYS
    }
    
    html_content = render_to_string('email/verification.html', context)
    text_content = f"Please verify your email by clicking: {verification_url}"
    
    msg = EmailMultiAlternatives(
        'Verify your Skillzone account',
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_password_reset_email(user, reset_url):
    """Send HTML password reset email"""
    context = {
        'user': user,
        'reset_url': reset_url
    }
    
    html_content = render_to_string('email/password_reset.html', context)
    text_content = f"Reset your password by clicking: {reset_url}"
    
    msg = EmailMultiAlternatives(
        'Reset your Skillzone password',
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
