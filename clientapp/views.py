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
    published = Articles.objects.filter(is_active=True).select_related('categorie')
    recent_articles = published.order_by('-date_publication')[:7]
    activity_articles = published.order_by('-date_publication')[:5]

    categories = Categories.objects.filter(
        articles__is_active=True
    ).distinct().order_by('nom')

    categories_with_articles = []
    for category in categories:
        articles = published.filter(categorie=category).order_by('-date_publication')
        if articles.exists():
            categories_with_articles.append({
                'category': category,
                'articles': articles,
            })

    return render(request, 'client/articles.html', {
        'departement': Departements.objects.all(),
        'recent_articles': recent_articles,
        'categories_with_articles': categories_with_articles,
        'categories': categories,
        'activity_articles': activity_articles,
        'total_count': published.count(),
    })

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

def articleDetailPage(request, id):
    article = get_object_or_404(Articles, id=id, is_active=True)
    related = Articles.objects.filter(
        categorie=article.categorie, is_active=True
    ).exclude(id=article.id).order_by('-date_publication')[:4]
    return render(request, 'client/article_detail.html', {
        'article': article,
        'related_articles': related,
        'departement': Departements.objects.all(),
    })