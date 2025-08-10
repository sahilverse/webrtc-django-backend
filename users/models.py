from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return f"{self.email} - ({self.first_name} {self.last_name})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        super.save(*args, **kwargs)
        
        if self.profile_image:
            img = Image.open(self.profile_image)
            
            max_size = (320, 320)
            
            if img.height > 320 or img.width > 320:
                img.thumbnail(max_size)
                
                img_io = BytesIO()
                img_format = img.format if img.format else 'JPEG'
                img.save(img_io, format=img_format, quality=85)
                
                
                self.profile_image.save(
                    self.profile_image.name,
                    ContentFile(img_io.getvalue()),
                    save=False
                )
                super().save(update_fields=['profile_image'])
        




