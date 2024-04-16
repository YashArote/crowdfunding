from django.conf import settings
from django.db import models

# Create your models here.
class Image(models.Model):
    image=models.ImageField(upload_to="images/%Y/%m/%d/")

class Address(models.Model):
    user=models.OneToOneField("auth.user",related_name="address",on_delete=models.CASCADE)
    address=models.CharField(max_length=100)
    
class Profile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,models.CASCADE)
    photo=models.ImageField(upload_to="users/%Y/%m/%d/",blank=True)
    
    def __str__(self):
        print(self.photo)
        return f'Profile of {self.user.username}'
    

class Approve(models.Model):
    camp_id=models.BigIntegerField()
    approved=models.BooleanField(default=False)
    rejected=models.BooleanField(default=False)