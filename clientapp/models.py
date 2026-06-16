from django.db import models
import uuid
from etudiantapp.models import *
from userapp.models import User

# Create your models here.

class Personnel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='personnel')
    nom = models.CharField(max_length=50) 
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    grade = models.CharField(max_length=50)
    fonction = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='personnel', null=True, blank=True)

class AffectionPersonnel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    departement = models.ForeignKey(Departements, on_delete=models.CASCADE)
    date_affectation = models.DateField(auto_now_add=True)
    date_fin_affectation = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.personnel.nom
    class Meta:
        verbose_name = 'AffectionPersonnel'
        verbose_name_plural = 'AffectionPersonnels'

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

class Categories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    def __str__(self):
        return self.nom
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Articles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    image = models.ImageField(upload_to='articles/')
    date_publication = models.DateTimeField(auto_now_add=True)
    auteur = models.CharField(max_length=100)
    categorie = models.ForeignKey(Categories, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    fichier = models.FileField(upload_to='articles/fichiers/', null=True, blank=True)
    is_payant = models.BooleanField(default=False)
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contact = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titre

    @property
    def whatsapp_digits(self):
        if self.contact:
            digits = ''.join(c for c in self.contact if c.isdigit())
            if digits:
                if digits.startswith('0'):
                    return '243' + digits[1:]
                if not digits.startswith('243'):
                    return '243' + digits
                return digits
        return '243812345678'

    def whatsapp_url(self):
        from urllib.parse import quote
        message = f"Bonjour, je souhaite obtenir le document « {self.titre} »."
        if self.prix:
            message += f" Prix indiqué : {self.prix} USD."
        return f"https://wa.me/{self.whatsapp_digits}?text={quote(message)}"
        
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'


class Commentaires(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    auteur = models.CharField(max_length=100)
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)