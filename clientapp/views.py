from django.shortcuts import render
from .models import *
from etudiantapp.models import *

# Create your views here.

def indexPage(request):
    personnel = Personnel.objects.all()
    departement = Departements.objects.all()
    return render(request, 'client/index.html', {'person':personnel, 'departement':departement})

def bibliothequePage(request):
    return render(request, 'client/bibliotheque.html')
