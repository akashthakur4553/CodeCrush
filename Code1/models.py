from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class profile(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    latitude = models.FloatField(null=True, blank=True)  # Store latitude
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name
