from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuration personnalisée de l'interface d'administration pour le modèle User
    
    Cette classe étend UserAdmin de Django pour inclure les champs spécifiques
    à notre modèle utilisateur personnalisé (rôle, téléphone, bio, etc.)
    
    L'interface permet aux administrateurs de:
    - Consulter la liste des utilisateurs avec filtrage par rôle et statut
    - Créer et modifier des utilisateurs avec tous leurs attributs
    - Gérer les permissions et les groupes
    """
    # Configuration de l'affichage de la liste des utilisateurs
    list_display = (
        'username',  # Nom d'utilisateur
        'email',     # Adresse email
        'first_name', # Prénom
        'last_name',  # Nom
        'role',       # Rôle (joueur, coach, statisticien)
        'is_staff'    # Statut d'administrateur
    )
    
    # Filtres disponibles dans la barre latérale
    list_filter = (
        'role',       # Filtrer par rôle
        'is_staff',   # Filtrer par statut administrateur
        'is_active'   # Filtrer par compte actif/inactif
    )
    
    # Organisation des champs dans le formulaire d'édition, regroupés par sections
    fieldsets = (
        # Section de base - identifiants
        (None, {
            'fields': ('username', 'password')
        }),
        
        # Section informations personnelles
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'bio', 'profile_picture')
        }),
        
        # Section rôle
        (_('Role'), {
            'fields': ('role',)
        }),
        
        # Section permissions
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        
        # Section dates importantes
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    # Champs utilisés pour la recherche d'utilisateurs
    search_fields = ('username', 'first_name', 'last_name', 'email')
