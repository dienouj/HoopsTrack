from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

# Create your models here.

class Team(models.Model):
    """
    Modèle pour les équipes de basketball
    
    Ce modèle stocke les informations de base sur les équipes, notamment
    leurs noms, logos, localisations, et définit les relations avec les coaches
    et les statisticiens associés à l'équipe.
    """
    # Informations de base de l'équipe
    name = models.CharField(max_length=100, unique=True)  # Nom de l'équipe (doit être unique)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)  # Logo de l'équipe
    city = models.CharField(max_length=100, blank=True, null=True)  # Ville de l'équipe
    description = models.TextField(blank=True, null=True)  # Description/historique de l'équipe
    
    # Champs de suivi temporel
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    
    # Relation avec le coach (une équipe a un seul coach)
    coach = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,  # Si le coach est supprimé, l'équipe reste mais sans coach
        null=True,
        blank=True,
        related_name='coached_team',  # Accès inverse: user.coached_team
        limit_choices_to={'role': User.COACH}  # Limite les choix aux utilisateurs avec le rôle 'coach'
    )
    
    # Relation avec les statisticiens (une équipe peut avoir plusieurs statisticiens)
    staff = models.ManyToManyField(
        User,
        related_name='staffed_teams',  # Accès inverse: user.staffed_teams
        limit_choices_to={'role': User.STATISTICIAN},  # Limite les choix aux utilisateurs avec le rôle 'statistician'
        blank=True
    )
    
    class Meta:
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        
    def __str__(self):
        """Représentation textuelle de l'équipe: nom de l'équipe"""
        return self.name


class Player(models.Model):
    """
    Modèle pour les joueurs de basketball
    
    Ce modèle stocke les informations détaillées sur les joueurs, incluant:
    - Leurs caractéristiques physiques (taille, poids, envergure)
    - Leur poste sur le terrain
    - Leur numéro de maillot
    - L'équipe à laquelle ils appartiennent
    
    Le modèle Player est relié au modèle User (relation one-to-one), où sont stockées
    les informations d'authentification et les données personnelles de base.
    """
    # Définition des constantes pour les différents postes
    POINT_GUARD = 'PG'      # Meneur
    SHOOTING_GUARD = 'SG'   # Arrière
    SMALL_FORWARD = 'SF'    # Ailier
    POWER_FORWARD = 'PF'    # Ailier fort
    CENTER = 'C'            # Pivot
    
    # Choix disponibles pour le champ de poste, avec traduction
    POSITION_CHOICES = [
        (POINT_GUARD, _('Point Guard')),       # Meneur
        (SHOOTING_GUARD, _('Shooting Guard')), # Arrière
        (SMALL_FORWARD, _('Small Forward')),   # Ailier
        (POWER_FORWARD, _('Power Forward')),   # Ailier fort
        (CENTER, _('Center')),                 # Pivot
    ]
    
    # Relation avec le modèle User (contient les informations d'authentification et les données personnelles de base)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,  # Si l'utilisateur est supprimé, le profil joueur l'est aussi
        related_name='player_profile',  # Accès inverse: user.player_profile
        limit_choices_to={'role': User.PLAYER}  # Limite les choix aux utilisateurs avec le rôle 'player'
    )
    
    # Relation avec l'équipe
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,  # Si l'équipe est supprimée, le joueur reste mais sans équipe
        null=True,
        blank=True,
        related_name='players'  # Accès inverse: team.players
    )
    
    # Caractéristiques spécifiques du joueur
    jersey_number = models.PositiveSmallIntegerField(null=True, blank=True)  # Numéro de maillot
    position = models.CharField(max_length=2, choices=POSITION_CHOICES, blank=True, null=True)  # Poste du joueur
    height = models.PositiveSmallIntegerField(help_text=_('Height in centimeters'), blank=True, null=True)  # Taille en cm
    weight = models.PositiveSmallIntegerField(help_text=_('Weight in kilograms'), blank=True, null=True)  # Poids en kg
    wingspan = models.PositiveSmallIntegerField(help_text=_('Wingspan in centimeters'), blank=True, null=True)  # Envergure en cm
    date_of_birth = models.DateField(blank=True, null=True)  # Date de naissance
    
    # Statut et métadonnées
    active = models.BooleanField(default=True)  # Joueur actif ou inactif
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    
    class Meta:
        verbose_name = _('Player')
        verbose_name_plural = _('Players')
        unique_together = ('team', 'jersey_number')  # Un numéro de maillot doit être unique dans une équipe
        
    def __str__(self):
        """
        Représentation textuelle du joueur: prénom nom #numéro - poste
        Exemple: 'John Doe #23 - Small Forward'
        """
        return f"{self.user.first_name} {self.user.last_name} #{self.jersey_number or 'N/A'} - {self.get_position_display() or 'N/A'}"
