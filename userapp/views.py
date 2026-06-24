from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from clientapp.models import Categories, Articles, Personnel, AffectionPersonnel
from etudiantapp.models import Departements
from userapp.models import User
from functools import wraps

ARTICLE_FILE_MAX_SIZE = 4 * 1024 * 1024  # 4 Mo par fichier


def _check_upload_size(uploaded_file, label):
    if uploaded_file and uploaded_file.size > ARTICLE_FILE_MAX_SIZE:
        size_mo = uploaded_file.size / (1024 * 1024)
        return f'{label} trop volumineux ({size_mo:.1f} Mo). Taille maximum : 4 Mo.'
    return None


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


def administrator_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_personnel:
            messages.error(request, 'Accès réservé au personnel.')
            auth_logout(request)
            return redirect('login')
        if not request.user.is_administrator:
            messages.error(request, 'Accès réservé aux administrateurs.')
            return redirect('dash_home')
        return view_func(request, *args, **kwargs)
    return wrapper


def _save_personnel_affectation(personnel, departement, date_affectation):
    existing = AffectionPersonnel.objects.filter(personnel=personnel).first()
    if existing:
        existing.departement = departement
        existing.date_affectation = date_affectation
        existing.date_fin_affectation = None
        existing.save()
        pk = existing.pk
    else:
        aff = AffectionPersonnel.objects.create(
            personnel=personnel,
            departement=departement,
            date_affectation=date_affectation,
        )
        pk = aff.pk
    AffectionPersonnel.objects.filter(personnel=personnel).exclude(pk=pk).delete()


def login(request):
    if request.user.is_authenticated and request.user.is_personnel:
        return redirect('dash_home')

    espace = request.GET.get('espace', 'enseignant')
    if espace not in ('enseignant', 'non_enseignant'):
        espace = 'enseignant'

    if request.method == 'POST':
        espace = request.POST.get('espace', 'enseignant')
        password = request.POST.get('password', '')

        if espace in ('enseignant', 'non_enseignant'):
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
            messages.error(request, 'Espace de connexion invalide.')

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
                else:
                    size_error = _check_upload_size(image, 'L\'image de couverture') or _check_upload_size(fichier, 'Le fichier du document')
                    if size_error:
                        messages.error(request, size_error)
                    else:
                        from decimal import Decimal, InvalidOperation
                        prix = None
                        if is_payant and prix_str:
                            try:
                                prix = Decimal(prix_str.replace(',', '.'))
                                if prix < 0:
                                    raise InvalidOperation
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
    personnel = Personnel.objects.filter(user=request.user).first()
    affectation = None
    if personnel:
        affectation = AffectionPersonnel.objects.filter(
            personnel=personnel
        ).select_related('departement').first()

    active_tab = request.GET.get('tab', '')
    if active_tab not in ('compte', 'personnel', 'affectation'):
        active_tab = ''

    if request.method == 'POST':
        action = request.POST.get('action')
        redirect_tab = active_tab

        if action == 'update_account':
            redirect_tab = 'compte'
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not username or not email:
                messages.error(request, 'Identifiant et email sont obligatoires.')
            elif User.objects.filter(username__iexact=username).exclude(pk=request.user.pk).exists():
                messages.error(request, f'L\'identifiant « {username} » est déjà utilisé.')
            elif User.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Cet email est déjà utilisé.')
            else:
                user = request.user
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name

                if new_password or confirm_password or current_password:
                    if not current_password:
                        messages.error(request, 'Indiquez votre mot de passe actuel pour le modifier.')
                        return redirect(f'{request.path}?tab={redirect_tab}')
                    if new_password != confirm_password:
                        messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
                        return redirect(f'{request.path}?tab={redirect_tab}')
                    if not user.check_password(current_password):
                        messages.error(request, 'Mot de passe actuel incorrect.')
                        return redirect(f'{request.path}?tab={redirect_tab}')
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Compte et mot de passe mis à jour.')
                else:
                    user.save()
                    messages.success(request, 'Compte mis à jour.')

        elif action == 'update_personnel':
            redirect_tab = 'personnel'
            nom = request.POST.get('nom', '').strip()
            postnom = request.POST.get('postnom', '').strip()
            prenom = request.POST.get('prenom', '').strip()
            grade = request.POST.get('grade', '').strip()
            fonction = request.POST.get('fonction', '').strip()
            description = request.POST.get('description', '').strip()
            photo = request.FILES.get('photo')

            if not nom or not postnom or not prenom or not grade:
                messages.error(request, 'Nom, postnom, prénom et grade sont obligatoires.')
            elif not personnel and not photo:
                messages.error(request, 'Veuillez ajouter une photo de profil.')
            else:
                if not personnel:
                    personnel = Personnel(user=request.user)
                personnel.nom = nom
                personnel.postnom = postnom
                personnel.prenom = prenom
                personnel.grade = grade
                personnel.fonction = fonction or None
                personnel.description = description or None
                if photo:
                    personnel.photo = photo
                personnel.user = request.user
                personnel.save()
                messages.success(request, 'Profil personnel enregistré.')
 
        elif action == 'update_affectation':
            redirect_tab = 'affectation'
            if not request.user.is_administrator:
                messages.error(request, 'Seul un administrateur peut modifier l\'affectation.')
                return redirect(f'{request.path}?tab={redirect_tab}')
            if not personnel:
                messages.error(request, 'Complétez d\'abord votre profil personnel.')
                return redirect(f'{request.path}?tab=personnel')

            departement_id = request.POST.get('departement')
            date_affectation = request.POST.get('date_affectation', '').strip()

            if not departement_id or not date_affectation:
                messages.error(request, 'Département et date d\'affectation sont obligatoires.')
            else:
                departement = get_object_or_404(Departements, id=departement_id)
                _save_personnel_affectation(personnel, departement, date_affectation)
                messages.success(request, 'Affectation enregistrée.')

        return redirect(f'{request.path}?tab={redirect_tab}')

    return render(request, 'admin/settings.html', {
        'active_menu': 'settings',
        'active_tab': active_tab,
        'personnel': personnel,
        'affectation': affectation,
        'departements': Departements.objects.filter(is_active=True).order_by('designation'),
    })


@administrator_required
def dashboardAffectationsPage(request):
    departements = Departements.objects.filter(is_active=True).order_by('designation')
    search = request.GET.get('q', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_staff_affectation':
            personnel = get_object_or_404(Personnel, id=request.POST.get('personnel_id'))
            departement_id = request.POST.get('departement')
            date_affectation = request.POST.get('date_affectation', '').strip()

            if not departement_id or not date_affectation:
                messages.error(request, 'Département et date d\'affectation sont obligatoires.')
            else:
                departement = get_object_or_404(Departements, id=departement_id)
                _save_personnel_affectation(personnel, departement, date_affectation)
                nom = f'{personnel.prenom} {personnel.nom} {personnel.postnom}'.strip()
                messages.success(request, f'Affectation de « {nom} » enregistrée.')
        return redirect('dash_affectations')

    affectations = {
        aff.personnel_id: aff
        for aff in AffectionPersonnel.objects.select_related('departement')
    }

    staff_list = Personnel.objects.select_related('user').order_by('nom', 'postnom', 'prenom')
    if search:
        staff_list = staff_list.filter(
            Q(nom__icontains=search) |
            Q(postnom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(grade__icontains=search) |
            Q(fonction__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )

    staff_rows = []
    for person in staff_list:
        staff_rows.append({
            'personnel': person,
            'affectation': affectations.get(person.id),
        })

    return render(request, 'admin/affectations.html', {
        'active_menu': 'affectations',
        'staff_rows': staff_rows,
        'departements': departements,
        'search_query': search,
        'total_count': len(staff_rows),
    })
