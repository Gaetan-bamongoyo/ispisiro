from django.shortcuts import render, redirect
from .models import *

# Create your views here.
def formulaire_etudiant(request):
    provinces = Provinces.objects.all()
    communes = Communes.objects.all()
    quartiers = Quartiers.objects.all()
    departements = Departements.objects.all()
    promotions = Promotions.objects.all()
    annees = AnneeAcademiques.objects.all()
    context = {
        'provinces': provinces,
        'communes': communes,
        'quartiers': quartiers,
        'departements': departements,
        'promotions': promotions,
        'annees': annees
    }
    return render(request, 'etudiant/informations.html', context)

def createEtudiant(request):
    provinces = Provinces.objects.all()
    communes = Communes.objects.all()
    quartiers = Quartiers.objects.all()
    departements = Departements.objects.all()
    promotions = Promotions.objects.all()
    annees = AnneeAcademiques.objects.all()
    context = {
        'provinces': provinces,
        'communes': communes,
        'quartiers': quartiers,
        'departements': departements,
        'promotions': promotions,
        'annees': annees
    }
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            photo = request.FILES.get('photo')
            matricule = request.POST.get('matricule')
            nom = request.POST.get('nom')
            postnom = request.POST.get('postnom')
            prenom = request.POST.get('prenom')
            lieunaissance = request.POST.get('lieunaissance')
            datenaissance = request.POST.get('datenaissance')
            sexe = request.POST.get('sexe')
            etat_civil = request.POST.get('etatcivil')
            nationalite = request.POST.get('nationalite')
            activite_professionnelle = request.POST.get('activiteprofessionnelle')
            nom_pere = request.POST.get('nompere')
            nom_mere = request.POST.get('nommere')
            province_origine = request.POST.get('provinceorigine')
            territoire = request.POST.get('territoire')
            numero = request.POST.get('numero')
            email = request.POST.get('email')
            telephone = request.POST.get('telephone')
            telephone_secondaire = request.POST.get('telephone_secondaire')
            code_postal = request.POST.get('code_postal')
            nom_ecole = request.POST.get('nomecole')
            section_suivi = request.POST.get('sectionsuivi')
            annee_diplome = request.POST.get('anneediplome')
            pourcentage_diplome = request.POST.get('pourcentage')
            numero_diplome = request.POST.get('numerodiplome')
            premier_choix = request.POST.get('departement')
            deuxieme_choix = request.POST.get('deuxiemechoix')
            
            # Validation des champs obligatoires minimaux
            if not all([matricule, nom, postnom, prenom]):
                context['error'] = "Veuillez remplir au minimum le matricule, nom, postnom et prénom."
                return render(request, 'etudiant/informations.html', context)
            
            # Conversion de la date (optionnelle)
            from datetime import datetime
            datenaissance_parsed = None
            if datenaissance:
                try:
                    datenaissance_parsed = datetime.strptime(datenaissance, '%d/%m/%Y').date()
                except ValueError:
                    context['error'] = "Format de date invalide. Utilisez DD/MM/YYYY"
                    return render(request, 'etudiant/informations.html', context)
            
            # Vérification si l'étudiant existe déjà
            if Etudiants.objects.filter(matricule=matricule).exists():
                context['error'] = f"Un étudiant avec le matricule {matricule} existe déjà."
                return render(request, 'etudiant/informations.html', context)
            
            # Création de l'étudiant
            etudiant = Etudiants.objects.create(
                matricule=matricule,
                nom=nom,
                postnom=postnom,
                prenom=prenom,
                lieunaissance=lieunaissance,
                datenaissance=datenaissance_parsed,
                sexe=sexe,
                etat_civil=etat_civil,
                nationalite=nationalite,
                activite_professionnelle=activite_professionnelle,
                nom_pere=nom_pere,
                nom_mere=nom_mere,
                province_origine=province_origine,
                territoire=territoire,
                numero=numero,
                email=email,
                telephone=int(telephone) if telephone else None,
                telephone_secondaire=int(telephone_secondaire) if telephone_secondaire else None,
                nom_ecole=nom_ecole,
                section_suivi=section_suivi,
                annee_diplome=annee_diplome,
                pourcentage_diplome=pourcentage_diplome,
                numero_diplome=numero_diplome,
                premier_choix=premier_choix,
                deuxieme_choix=deuxieme_choix,
                photo=photo,
                # Valeurs par défaut pour les champs manquants dans le modèle
                quartier=quartiers.first() if quartiers.exists() else None
            )
            
            # Redirection vers la page de succès
            return redirect('etudiantapp:succes', etudiant_id=etudiant.id)
            
        except Exception as e:
            context['error'] = f"Erreur lors de la création: {str(e)}"
    
    return render(request, 'etudiant/informations.html', context)

def inscrireEtudiant(request):
    """Vue pour inscrire un étudiant existant"""
    departements = Departements.objects.all()
    promotions = Promotions.objects.all()
    annees = AnneeAcademiques.objects.all()
    etudiants = Etudiants.objects.all()
    
    context = {
        'departements': departements,
        'promotions': promotions,
        'annees': annees,
        'etudiants': etudiants
    }
    
    if request.method == 'POST':
        try:
            etudiant_id = request.POST.get('etudiant')
            departement_id = request.POST.get('departement')
            promotion_id = request.POST.get('promotion')
            anneeacademique_id = request.POST.get('anneeacademique')
            
            # Validation des champs obligatoires
            if not all([etudiant_id, departement_id, promotion_id, anneeacademique_id]):
                context['error'] = "Veuillez remplir tous les champs obligatoires."
                return render(request, 'etudiant/inscription.html', context)
            
            # Récupération des objets
            etudiant = Etudiants.objects.get(id=etudiant_id)
            departement = Departements.objects.get(id=departement_id)
            promotion = Promotions.objects.get(id=promotion_id)
            anneeacademique = AnneeAcademiques.objects.get(id=anneeacademique_id)
            
            # Vérification si l'inscription existe déjà
            if Inscriptions.objects.filter(
                etudiant=etudiant, 
                departement=departement, 
                promotion=promotion, 
                anneeacademique=anneeacademique
            ).exists():
                context['error'] = f"L'étudiant {etudiant.nom} {etudiant.postnom} {etudiant.prenom} est déjà inscrit dans ce programme pour cette année."
                return render(request, 'etudiant/inscription.html', context)
            
            # Création de l'inscription
            inscription = Inscriptions.objects.create(
                etudiant=etudiant,
                departement=departement,
                promotion=promotion,
                anneeacademique=anneeacademique,
                is_active=True
            )
            
            context['success'] = f"Étudiant {etudiant.nom} {etudiant.postnom} {etudiant.prenom} inscrit avec succès!"
            context['inscription'] = inscription
            
        except Etudiants.DoesNotExist:
            context['error'] = "Étudiant non trouvé."
        except Departements.DoesNotExist:
            context['error'] = "Département non trouvé."
        except Promotions.DoesNotExist:
            context['error'] = "Promotion non trouvée."
        except AnneeAcademiques.DoesNotExist:
            context['error'] = "Année académique non trouvée."
        except Exception as e:
            context['error'] = f"Erreur lors de l'inscription: {str(e)}"
    
    return render(request, 'etudiant/inscription.html', context)

def listeEtudiants(request):
    """Vue pour afficher la liste des étudiants"""
    etudiants = Etudiants.objects.all().order_by('-id')
    inscriptions = Inscriptions.objects.filter(is_active=True)
    
    context = {
        'etudiants': etudiants,
        'inscriptions': inscriptions
    }
    
    return render(request, 'etudiant/liste.html', context)

def pageSucces(request, etudiant_id):
    """Vue pour afficher la page de succès après inscription"""
    try:
        etudiant = Etudiants.objects.get(id=etudiant_id)
        context = {
            'etudiant': etudiant
        }
        return render(request, 'etudiant/succes.html', context)
    except Etudiants.DoesNotExist:
        return redirect('etudiantapp:formulaire')
