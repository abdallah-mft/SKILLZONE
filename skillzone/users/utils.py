import os
import uuid
from PIL import Image
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

def handle_avatar_upload(image_file, user_id):
    """
    Handle avatar image upload, including validation and processing
    """
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if not hasattr(image_file, 'content_type') or image_file.content_type not in allowed_types:
        raise ValueError('Invalid file type. Only JPEG, PNG and GIF are allowed.')

    # Validate file size (max 5MB)
    if image_file.size > 5 * 1024 * 1024:
        raise ValueError('File too large. Maximum size is 5MB.')

    # Generate unique filename
    ext = os.path.splitext(image_file.name)[1].lower()
    filename = f'avatar_{user_id}_{uuid.uuid4().hex[:8]}{ext}'
    
    # Create upload path
    upload_path = os.path.join('avatars', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, 'avatars', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Process and save image
    try:
        with Image.open(image_file) as img:
            # Convert to RGB if necessary
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Resize if too large (max 800x800)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))
            
            # Save processed image
            img.save(full_path, quality=85, optimize=True)
            
        return upload_path
        
    except Exception as e:
        logger.error(f"Error processing avatar image: {str(e)}")
        if os.path.exists(full_path):
            os.remove(full_path)
        raise ValueError('Error processing image file')

def send_verification_email(user):
    """Send verification code via email"""
    verification_code = user.profile.generate_verification_code()
    subject = 'Verify your Skillzone account'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    context = {
        'user': user,
        'verification_code': verification_code,
    }
    
    # Render email templates
    html_content = render_to_string('email/verification.html', context)
    text_content = f"Your verification code is: {verification_code}"
    
    # Create email message
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send(fail_silently=False)
        logger.info(f"Verification email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {str(e)}")
        raise

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





