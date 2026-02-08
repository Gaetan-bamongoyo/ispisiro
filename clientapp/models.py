from django.db import models

# Create your models here.

class Personnel(models.Model):
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    grade = models.CharField(max_length=50)
    degre = models.CharField(max_length=50)
    description = models.TextField()
    photo = models.ImageField(upload_to='personnel')
