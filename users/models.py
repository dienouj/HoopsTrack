from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec contrôle d'accès basé sur les rôles pour HoopTrack
    
    Ce modèle étend l'AbstractUser de Django pour ajouter des fonctionnalités spécifiques
    à l'application HoopTrack, notamment les rôles, informations personnelles additionnelles
    et image de profil.
    
    Rôles:
    - Joueur: Peut voir ses propres statistiques et les moyennes d'équipe
    - Coach: Peut voir toutes les statistiques de l'équipe
    - Statisticien: Peut ajouter/modifier les performances des joueurs
    """
    # Définition des constantes pour les différents rôles
    PLAYER = 'player'
    COACH = 'coach'
    STATISTICIAN = 'statistician'
    
    # Choix disponibles pour le champ de rôle, avec traduction
    ROLE_CHOICES = [
        (PLAYER, _('Player')),         # Joueur
        (COACH, _('Coach')),           # Entraîneur
        (STATISTICIAN, _('Statistician')), # Statisticien
    ]
    
    # Champs personnalisés ajoutés au modèle utilisateur
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=PLAYER,
        help_text=_('Role determines permissions in the system')  # Le rôle détermine les permissions dans le système
    )
    # Numéro de téléphone (optionnel)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Biographie (optionnelle)
    bio = models.TextField(blank=True, null=True)
    
    # Photo de profil (optionnelle)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        
    def __str__(self):
        """Représentation textuelle de l'utilisateur: prénom nom (rôle)"""
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"
    
    # Propriétés pour vérifier facilement le rôle de l'utilisateur
    @property
    def is_player(self):
        """Vérifie si l'utilisateur est un joueur"""
        return self.role == self.PLAYER
    
    @property
    def is_coach(self):
        """Vérifie si l'utilisateur est un coach"""
        return self.role == self.COACH
    
    @property
    def is_statistician(self):
        """Vérifie si l'utilisateur est un statisticien"""
        return self.role == self.STATISTICIAN
