from django.db import models
import uuid

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

class Blog(models.Model):
    titre = models.CharField(max_length=255)
    categorie = models.CharField(max_length=100, help_text="Ex: Événement, Académique, Campus")
    auteur = models.CharField(max_length=100, default="Admin")
    image = models.ImageField(upload_to='blog/')
    date_publication = models.DateTimeField(auto_now_add=True)
    description_courte = models.TextField(help_text="Introduction affichée sur la page d'accueil")
    contenu = models.TextField(help_text="Contenu complet de l'article/événement")
    
    # Champs optionnels pour les détails de l'événement vus dans le design
    citation = models.TextField(null=True, blank=True, help_text="Optionnel: Citation mise en évidence")
    auteur_citation = models.CharField(max_length=100, null=True, blank=True)
    
    # Détails Sidebar (Lieu, Heure, etc.)
    lieu = models.CharField(max_length=255, null=True, blank=True)
    heure = models.CharField(max_length=100, null=True, blank=True, help_text="Ex: 08h00 - 16h00")
    entree = models.CharField(max_length=100, null=True, blank=True, help_text="Ex: Libre sur inscription")

    def __str__(self):
        return self.titre
