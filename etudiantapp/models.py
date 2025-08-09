from django.db import models

# Create your models here.

class Etudiants(models.Model):
    numero_enregistrement = models.CharField(max_length=50)
    matricule = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    lieunaissance = models.CharField(max_length=50)
    datenaissance = models.DateField()
    sexe = models.CharField(max_length=2)
    etat_civil = models.CharField(max_length=50)
    nationalite = models.CharField(max_length=50)
    nom_pere = models.CharField(max_length=50, null=True)
    nom_mere = models.CharField(max_length=50, null=True)
    province_origine = models.CharField(max_length=50, null=True)
    territoire = models.CharField(max_length=50, null=True)
    adresse = models.CharField(max_length=50, null=True)
    nom_ecole = models.CharField(max_length=50)
    section_suivi = models.CharField(max_length=50)
    annee_diplome = models.CharField(max_length=50)
    pourcentage_diplome = models.CharField(max_length=50)
    numero_diplome = models.CharField(max_length=50, null=True)
    activite_professionnelle = models.CharField(max_length=50, null=True)
    premier_choix = models.CharField(max_length=50)
    deuxieme_choix = models.CharField(max_length=50)
    dossier = models.TextField()

class Departements(models.Model):
    designation = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

class Promotions(models.Model):
    designation = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

class AnneeAcademiques(models.Model):
    designation = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

class Inscriptions(models.Model):
    departement = models.ForeignKey(Departements, on_delete=models.CASCADE, related_name='departement')
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, related_name='promotion')
    etudiant = models.ForeignKey(Etudiants, on_delete=models.CASCADE, related_name='etudiant')
    anneeacademique = models.ForeignKey(AnneeAcademiques, on_delete=models.CASCADE, related_name='anneeacademique')
    date_inscription = models.DateField(auto_now_add=True)
    is_active = models.BooleanField()

