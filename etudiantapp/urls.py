from django.urls import path
from .views import *

app_name = 'etudiantapp'
urlpatterns = [
    path('formulaire', formulaire_etudiant, name='formulaire'),
    path('create', createEtudiant, name='create'),
    path('inscription', inscrireEtudiant, name='inscription'),
    path('liste', listeEtudiants, name='liste'),
    path('succes/<int:etudiant_id>', pageSucces, name='succes')
]
