from django.db import models

# Create your models here.
class Provinces(models.Model):
    designation = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

class Communes(models.Model):
    designation = models.CharField(max_length=50)
    province = models.ForeignKey(Provinces, on_delete=models.CASCADE, related_name='province')
    is_active = models.BooleanField(default=True)

class Quartiers(models.Model):
    designation = models.CharField(max_length=50)
    commune = models.ForeignKey(Communes, on_delete=models.CASCADE, related_name='commune')
    is_active = models.BooleanField(default=True)

class Etudiants(models.Model):
    matricule = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    lieunaissance = models.CharField(max_length=50)
    datenaissance = models.DateField()
    sexe = models.CharField(max_length=2)
    etat_civil = models.CharField(max_length=50, null=True)
    nationalite = models.CharField(max_length=50, null=True)
    nom_pere = models.CharField(max_length=50, null=True)
    nom_mere = models.CharField(max_length=50, null=True)
    province_origine = models.CharField(max_length=50, null=True)
    territoire = models.CharField(max_length=50, null=True)
    numero = models.IntegerField(null=True)
    avenue = models.CharField(max_length=50, null=True)
    nom_ecole = models.CharField(max_length=50, null=True)
    section_suivi = models.CharField(max_length=50, null=True)
    annee_diplome = models.CharField(max_length=50, null=True)
    pourcentage_diplome = models.CharField(max_length=50, null=True)
    numero_diplome = models.CharField(max_length=50, null=True)
    activite_professionnelle = models.CharField(max_length=50, null=True)
    premier_choix = models.CharField(max_length=50, null=True)
    deuxieme_choix = models.CharField(max_length=50, null=True)
    dossier = models.TextField(null=True)
    photo = models.ImageField(upload_to='etudiant')
    email = models.EmailField(max_length=254, null=True)
    telephone = models.IntegerField(null=True)
    telephone_secondaire = models.IntegerField(null=True)
    quartier = models.ForeignKey(Quartiers, on_delete=models.CASCADE, related_name='quartier')

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


