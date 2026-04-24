from django.shortcuts import render, get_object_or_404
from .models import *
from etudiantapp.models import *
from ispisiro.utils import *

# Create your views here.

def indexPage(request):
    personnel = Personnel.objects.all()
    departement = Departements.objects.all()
    comite = Comite.objects.all()
    blogs = Blog.objects.all().order_by('-date_publication')

    for i in blogs:
        i.encrypt_id = encrypt_id(i.id)

    return render(request, 'client/index.html', {
        'person': personnel, 
        'departement': departement, 
        'comite': comite,
        'blogs': blogs
    })

def bibliothequePage(request):
    return render(request, 'client/bibliotheque.html')

def bloqPage(request, id):
    id_pk = decrypt_id(id)
    blog = get_object_or_404(Blog, id=id_pk)
    recent_blogs = Blog.objects.exclude(id=id_pk).order_by('-date_publication')[:3]
    return render(request, 'client/bloq.html', {
        'blog': blog,
        'recent_blogs': recent_blogs
    })

def detail_filierePage(request, id):
    filiere = get_object_or_404(Departements, id=id)
    departements = Departements.objects.all() # For footer
    return render(request, 'client/detail_filiere.html', {
        'filiere': filiere,
        'departement': departements
    })
