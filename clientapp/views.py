from django.shortcuts import render
from .models import *
from etudiantapp.models import *

# Create your views here.

def indexPage(request):
    personnel = Personnel.objects.all()
    departement = Departements.objects.all()
    comite = Comite.objects.all()
    blogs = Blog.objects.all().order_by('-date_publication')
    return render(request, 'client/index.html', {
        'person': personnel, 
        'departement': departement, 
        'comite': comite,
        'blogs': blogs
    })

def bibliothequePage(request):
    return render(request, 'client/bibliotheque.html')

from django.shortcuts import render, get_object_or_404

def bloqPage(request, id):
    blog = get_object_or_404(Blog, id=id)
    recent_blogs = Blog.objects.exclude(id=id).order_by('-date_publication')[:3]
    return render(request, 'client/bloq.html', {
        'blog': blog,
        'recent_blogs': recent_blogs
    })
