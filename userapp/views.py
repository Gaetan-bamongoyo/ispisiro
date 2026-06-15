from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from clientapp.models import Categories, Articles
from userapp.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from functools import wraps


def personnel_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_personnel:
            messages.error(request, 'Accès réservé au personnel.')
            auth_logout(request)
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def login(request):
    if request.user.is_authenticated and request.user.is_personnel:
        return redirect('dash_home')

    espace = request.GET.get('espace', 'etudiant')

    if request.method == 'POST':
        espace = request.POST.get('espace', 'etudiant')
        password = request.POST.get('password', '')

        if espace == 'personnel':
            identifiant = request.POST.get('email', '').strip()
            if not identifiant or not password:
                messages.error(request, 'Email et mot de passe requis.')
            else:
                user_obj = User.objects.filter(
                    Q(email__iexact=identifiant) | Q(username__iexact=identifiant),
                    is_personnel=True,
                ).first()
                if not user_obj:
                    messages.error(request, 'Identifiants incorrects ou compte non autorisé.')
                else:
                    user = authenticate(request, username=user_obj.username, password=password)
                    if user is not None:
                        auth_login(request, user)
                        if not request.POST.get('remember'):
                            request.session.set_expiry(0)
                        return redirect('dash_home')
                    messages.error(request, 'Identifiants incorrects.')
        else:
            messages.info(request, 'La connexion étudiant sera disponible prochainement.')

    return render(request, 'login/signin.html', {'espace': espace})


def logout(request):
    auth_logout(request)
    return redirect('login')


def register(request):
    """Inscription réservée au personnel (enseignants / administratif)."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'Tous les champs sont obligatoires.')
        elif password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, f'L\'identifiant « {username} » est déjà utilisé.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        else:
            is_administrator = password == '@admin123'
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_personnel=True,
                is_etudiant=False,
                is_administrator=is_administrator,
            )
            auth_login(request, user)
            return redirect('dash_home')

    return render(request, 'login/signup.html', {'page_type': 'personnel'})

def _dash_stats():
    pending = Articles.objects.filter(is_active=False)
    return {
        'total_ouvrages': Articles.objects.filter(is_active=True).count(),
        'pending_ouvrages': pending.count(),
        'total_categories': Categories.objects.count(),
        'pending_list': pending.select_related('categorie').order_by('-date_publication')[:5],
    }


@personnel_required
def dashboardPage(request):
    stats = _dash_stats()
    return render(request, 'admin/dashboard.html', {
        'active_menu': 'dashboard',
        **stats,
        'recent_articles': Articles.objects.select_related('categorie').order_by('-date_publication')[:5],
    })

@personnel_required
def dashboardOuvragesPage(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'add_category':
                nom = request.POST.get('nom', '').strip()
                if not nom:
                    messages.error(request, 'Le nom de la catégorie est obligatoire.')
                elif Categories.objects.filter(nom__iexact=nom).exists():
                    messages.error(request, f'La catégorie « {nom} » existe déjà.')
                else:
                    Categories.objects.create(nom=nom)
                    messages.success(request, f'Catégorie « {nom} » enregistrée.')
                return redirect('dash_ouvrages')

            if action == 'delete_category':
                category = get_object_or_404(Categories, id=request.POST.get('category_id'))
                if category.articles_set.exists():
                    messages.error(
                        request,
                        f'Impossible de supprimer « {category.nom} » : des ouvrages y sont rattachés.'
                    )
                else:
                    nom = category.nom
                    category.delete()
                    messages.success(request, f'Catégorie « {nom} » supprimée.')
                return redirect('dash_ouvrages')

            if action == 'add_article':
                titre = request.POST.get('titre', '').strip()
                auteur = request.POST.get('auteur', '').strip()
                contenu = request.POST.get('contenu', '').strip()
                categorie_id = request.POST.get('categorie')
                image = request.FILES.get('image')
                fichier = request.FILES.get('fichier')
                publier = request.POST.get('publier') == 'on'
                is_payant = request.POST.get('is_payant') == 'on'
                contact = request.POST.get('contact', '').strip()
                prix_str = request.POST.get('prix', '').strip()

                if not titre or not auteur or not contenu or not categorie_id:
                    messages.error(request, 'Titre, auteur, contenu et catégorie sont obligatoires.')
                elif not image:
                    messages.error(request, 'Veuillez choisir une image de couverture.')
                elif is_payant and not contact:
                    messages.error(request, 'Le numéro WhatsApp de contact est obligatoire pour un document payant.')
                elif is_payant and not fichier:
                    messages.error(request, 'Veuillez joindre le fichier du document.')
                else:
                    from decimal import Decimal, InvalidOperation
                    prix = None
                    if is_payant and prix_str:
                        try:
                            prix = Decimal(prix_str.replace(',', '.'))
                        except InvalidOperation:
                            messages.error(request, 'Prix invalide.')
                            return redirect('dash_ouvrages')

                    categorie = get_object_or_404(Categories, id=categorie_id)
                    Articles.objects.create(
                        titre=titre,
                        auteur=auteur,
                        contenu=contenu,
                        categorie=categorie,
                        image=image,
                        fichier=fichier,
                        is_active=publier,
                        is_payant=is_payant,
                        prix=prix if is_payant else None,
                        contact=contact if is_payant else None,
                        user=request.user,
                    )
                    if publier:
                        messages.success(request, f'Ouvrage « {titre} » enregistré et publié.')
                    else:
                        messages.success(request, f'Ouvrage « {titre} » enregistré (en attente de validation).')
                return redirect('dash_ouvrages')

            if action == 'validate_article':
                article = get_object_or_404(Articles, id=request.POST.get('article_id'))
                article.is_active = True
                article.save()
                messages.success(request, f'Ouvrage « {article.titre} » validé et publié.')
                return redirect('dash_ouvrages')

            if action == 'reject_article':
                article = get_object_or_404(Articles, id=request.POST.get('article_id'))
                titre = article.titre
                article.delete()
                messages.warning(request, f'Ouvrage « {titre} » refusé et supprimé.')
                return redirect('dash_ouvrages')

            if action == 'unpublish_article':
                article = get_object_or_404(Articles, id=request.POST.get('article_id'))
                article.is_active = False
                article.save()
                messages.info(request, f'Ouvrage « {article.titre} » retiré de la publication.')
                return redirect('dash_ouvrages')

            if action == 'delete_article':
                article = get_object_or_404(Articles, id=request.POST.get('article_id'))
                titre = article.titre
                article.delete()
                messages.warning(request, f'Ouvrage « {titre} » supprimé.')
                return redirect('dash_ouvrages')

        stats = _dash_stats()
        categories = Categories.objects.all().order_by('nom')
        search = request.GET.get('q', '').strip()
        # verifier si l'utilisateur est administrateur
        if request.user.is_administrator:
            articles = Articles.objects.all().order_by('-date_publication')
        else:
            articles = Articles.objects.filter(user=request.user).order_by('-date_publication')

        if search:
            articles = articles.filter(
                Q(titre__icontains=search) |
                Q(auteur__icontains=search) |
                Q(categorie__nom__icontains=search) |
                Q(contenu__icontains=search)
            )

        return render(request, 'admin/ouvrages.html', {
            'active_menu': 'ouvrages',
            'categories': categories,
            'articles': articles,
            'search_query': search,
            **stats,
        })

@personnel_required
def dashboardCoursPage(request):
    return render(request, 'admin/cours.html', {'active_menu': 'cours'})


@personnel_required
def dashboardEtudiantsPage(request):
    return render(request, 'admin/etudiants.html', {'active_menu': 'etudiants'})

@personnel_required
def dashboardSettingsPage(request):
    return render(request, 'admin/settings.html', {'active_menu': 'settings'})
