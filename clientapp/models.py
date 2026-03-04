from django.db import models

# Create your models here.

class Personnel(models.Model):
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    grade = models.CharField(max_length=50)
    fonction = models.CharField(max_length=50, null=True)
    description = models.TextField(null=True)
    photo = models.ImageField(upload_to='personnel')

class Comite(models.Model):
    poste = models.CharField(max_length=50)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    is_active = models.BooleanField()
