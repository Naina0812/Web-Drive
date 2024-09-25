from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Entity(models.Model):
    folder_path = models.TextField()
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    hashpath = models.CharField(max_length=255)
    is_folder = models.BooleanField()
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    user_id = models.IntegerField(default=0)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name