from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    is_registered = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class Property(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    place = models.CharField(max_length=255)
    area = models.FloatField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    nearby_hospitals = models.CharField(max_length=255)
    nearby_colleges = models.CharField(max_length=255)
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    likes = models.ManyToManyField(CustomUser, related_name='liked_properties', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title
