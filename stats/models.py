from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from teams.models import Team, Player

class Game(models.Model):
    """
    Modèle pour les matchs de basketball
    
    Ce modèle stocke toutes les informations relatives à un match:
    - Les équipes qui s'affrontent (domicile et extérieur)
    - La date, l'heure et le lieu du match
    - Le score final
    - Le statut du match (planifié, en direct, terminé, annulé)
    
    Les performances individuelles des joueurs sont liées à ce modèle
    via une relation inverse depuis le modèle Performance.
    """
    # Informations sur les équipes participant au match
    home_team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE,  # Si l'équipe est supprimée, ses matchs le sont aussi
        related_name='home_games'  # Accès inverse: team.home_games (matchs à domicile)
    )
    away_team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE,
        related_name='away_games'  # Accès inverse: team.away_games (matchs à l'extérieur)
    )
    
    # Date et lieu du match
    date = models.DateField()  # Date du match
    time = models.TimeField()  # Heure du match
    location = models.CharField(max_length=255)  # Lieu du match (nom de la salle)
    
    # Score final du match
    home_score = models.PositiveIntegerField(null=True, blank=True)  # Score de l'équipe à domicile
    away_score = models.PositiveIntegerField(null=True, blank=True)  # Score de l'équipe à l'extérieur
    
    # Définition des constantes pour les différents statuts de match
    SCHEDULED = 'scheduled'  # Match planifié
    LIVE = 'live'  # Match en cours
    COMPLETED = 'completed'  # Match terminé
    CANCELLED = 'cancelled'  # Match annulé
    
    # Choix disponibles pour le champ de statut, avec traduction
    STATUS_CHOICES = [
        (SCHEDULED, _('Scheduled')),  # Planifié
        (LIVE, _('Live')),  # En direct
        (COMPLETED, _('Completed')),  # Terminé
        (CANCELLED, _('Cancelled')),  # Annulé
    ]
    
    # Statut actuel du match
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=SCHEDULED  # Par défaut, un match est en statut "planifié"
    )
    
    # Métadonnées du match
    notes = models.TextField(blank=True, null=True)  # Notes additionnelles sur le match
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création de l'entrée
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    
    class Meta:
        verbose_name = _('Game')
        verbose_name_plural = _('Games')
        ordering = ['-date', '-time']  # Tri par date et heure décroissantes (les plus récents d'abord)
    
    def __str__(self):
        """
        Représentation textuelle du match: équipe domicile vs équipe extérieur (date)
        Exemple: 'Lakers vs Bulls (2025-01-15)'
        """
        return f"{self.home_team} vs {self.away_team} ({self.date})"
    
    @property
    def is_completed(self):
        """Vérifie si le match est terminé"""
        return self.status == self.COMPLETED
    
    @property
    def winner(self):
        """
        Détermine l'équipe gagnante du match
        
        Retourne:
        - L'équipe gagnante (Team) si le match est terminé et qu'il y a un gagnant
        - None si le match n'est pas terminé, si les scores sont égaux (match nul),
          ou si les scores ne sont pas encore enregistrés
        """
        if not self.is_completed or self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None  # Match nul


class Performance(models.Model):
    """
    Modèle pour les performances individuelles des joueurs lors d'un match
    
    Ce modèle stocke toutes les statistiques d'un joueur pour un match spécifique:
    - Points, rebonds, passes décisives, interceptions, contres
    - Pourcentages de réussite aux tirs (2pts, 3pts, lancers francs)
    - Minutes jouées, fautes personnelles, ballons perdus
    
    Ces statistiques sont enregistrées par un statisticien après le match.
    """
    # Relations avec joueur et match
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,  # Si le joueur est supprimé, ses performances le sont aussi
        related_name='performances'  # Accès inverse: player.performances
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,  # Si le match est supprimé, les performances associées le sont aussi
        related_name='performances'  # Accès inverse: game.performances
    )
    
    # Temps de jeu
    minutes_played = models.PositiveSmallIntegerField(
        default=0, 
        help_text=_('Minutes played in the game')  # Minutes jouées dans le match
    )
    
    # Statistiques de scoring
    points = models.PositiveSmallIntegerField(default=0)  # Points marqués
    field_goals_made = models.PositiveSmallIntegerField(default=0)  # Tirs à 2pts réussis
    field_goals_attempted = models.PositiveSmallIntegerField(default=0)  # Tirs à 2pts tentés
    three_pointers_made = models.PositiveSmallIntegerField(default=0)  # Tirs à 3pts réussis
    three_pointers_attempted = models.PositiveSmallIntegerField(default=0)  # Tirs à 3pts tentés
    free_throws_made = models.PositiveSmallIntegerField(default=0)  # Lancers francs réussis
    free_throws_attempted = models.PositiveSmallIntegerField(default=0)  # Lancers francs tentés
    
    # Statistiques de rebonds
    offensive_rebounds = models.PositiveSmallIntegerField(default=0)  # Rebonds offensifs
    defensive_rebounds = models.PositiveSmallIntegerField(default=0)  # Rebonds défensifs
    
    # Autres statistiques
    assists = models.PositiveSmallIntegerField(default=0)  # Passes décisives
    steals = models.PositiveSmallIntegerField(default=0)  # Interceptions
    blocks = models.PositiveSmallIntegerField(default=0)  # Contres
    turnovers = models.PositiveSmallIntegerField(default=0)  # Ballons perdus
    personal_fouls = models.PositiveSmallIntegerField(default=0)  # Fautes personnelles
    
    # Métadonnées de la performance
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,  # Si l'utilisateur est supprimé, garder qui a créé la stat devient NULL
        null=True,
        blank=True,
        related_name='recorded_performances',  # Accès inverse: user.recorded_performances
        limit_choices_to={'role': 'statistician'}  # Seul un statisticien peut enregistrer des performances
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    notes = models.TextField(blank=True, null=True)  # Notes sur la performance
    
    class Meta:
        verbose_name = _('Performance')
        verbose_name_plural = _('Performances')
        # Un joueur ne peut avoir qu'une seule entrée de performance par match
        unique_together = ('player', 'game')
        
    def __str__(self):
        """
        Représentation textuelle de la performance: joueur - match
        Exemple: 'Michael Jordan #23 - Bulls vs Lakers (2025-01-15)'
        """
        return f"{self.player} - {self.game}"
    
    @property
    def total_rebounds(self):
        """
        Calcule le nombre total de rebonds (offensifs + défensifs)
        """
        return self.offensive_rebounds + self.defensive_rebounds
    
    @property
    def field_goal_percentage(self):
        """
        Calcule le pourcentage de réussite aux tirs à 2 points
        
        Retourne:
        - Le pourcentage arrondi à une décimale si des tirs ont été tentés
        - None si aucun tir n'a été tenté
        """
        if self.field_goals_attempted == 0:
            return None
        return round((self.field_goals_made / self.field_goals_attempted) * 100, 1)
    
    @property
    def three_point_percentage(self):
        """
        Calcule le pourcentage de réussite aux tirs à 3 points
        
        Retourne:
        - Le pourcentage arrondi à une décimale si des tirs ont été tentés
        - None si aucun tir n'a été tenté
        """
        if self.three_pointers_attempted == 0:
            return None
        return round((self.three_pointers_made / self.three_pointers_attempted) * 100, 1)
    
    @property
    def free_throw_percentage(self):
        """
        Calcule le pourcentage de réussite aux lancers francs
        
        Retourne:
        - Le pourcentage arrondi à une décimale si des lancers ont été tentés
        - None si aucun lancer n'a été tenté
        """
        if self.free_throws_attempted == 0:
            return None
        return round((self.free_throws_made / self.free_throws_attempted) * 100, 1)


class TeamPerformance(models.Model):
    """
    Modèle pour les performances d'équipe lors d'un match
    
    Ce modèle stocke les statistiques collectives d'une équipe pour un match spécifique,
    notamment le total de points, rebonds, passes, interceptions, etc.
    
    Ces statistiques sont calculées automatiquement à partir des performances
    individuelles des joueurs ou saisies manuellement par un statisticien.
    """
    # Relations avec équipe et match
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,  # Si l'équipe est supprimée, ses performances le sont aussi
        related_name='team_performances'  # Accès inverse: team.team_performances
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,  # Si le match est supprimé, les performances associées le sont aussi
        related_name='team_performances'  # Accès inverse: game.team_performances
    )
    
    # Statistiques d'équipe
    points = models.PositiveSmallIntegerField(default=0)  # Points marqués par l'équipe
    field_goals_made = models.PositiveSmallIntegerField(default=0)  # Tirs à 2pts réussis
    field_goals_attempted = models.PositiveSmallIntegerField(default=0)  # Tirs à 2pts tentés
    three_pointers_made = models.PositiveSmallIntegerField(default=0)  # Tirs à 3pts réussis
    three_pointers_attempted = models.PositiveSmallIntegerField(default=0)  # Tirs à 3pts tentés
    free_throws_made = models.PositiveSmallIntegerField(default=0)  # Lancers francs réussis
    free_throws_attempted = models.PositiveSmallIntegerField(default=0)  # Lancers francs tentés
    
    # Autres statistiques collectives
    offensive_rebounds = models.PositiveSmallIntegerField(default=0)  # Rebonds offensifs
    defensive_rebounds = models.PositiveSmallIntegerField(default=0)  # Rebonds défensifs
    assists = models.PositiveSmallIntegerField(default=0)  # Passes décisives
    steals = models.PositiveSmallIntegerField(default=0)  # Interceptions
    blocks = models.PositiveSmallIntegerField(default=0)  # Contres
    turnovers = models.PositiveSmallIntegerField(default=0)  # Ballons perdus
    personal_fouls = models.PositiveSmallIntegerField(default=0)  # Fautes personnelles
    
    # Métadonnées
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,  # Si l'utilisateur est supprimé, garder qui a créé la stat devient NULL
        null=True,
        blank=True,
        related_name='recorded_team_performances',  # Accès inverse: user.recorded_team_performances
        limit_choices_to={'role': 'statistician'}  # Seul un statisticien peut enregistrer des stats d'équipe
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de dernière modification
    notes = models.TextField(blank=True, null=True)  # Notes sur la performance d'équipe
    
    class Meta:
        verbose_name = _('Team Performance')
        verbose_name_plural = _('Team Performances')
        # Une équipe ne peut avoir qu'une seule entrée de performance par match
        unique_together = ('team', 'game')
        
    def __str__(self):
        """
        Représentation textuelle de la performance d'équipe: équipe - match
        Exemple: 'Bulls - Bulls vs Lakers (2025-01-15)'
        """
        return f"{self.team} - {self.game}"
    
    @property
    def total_rebounds(self):
        """
        Calcule le nombre total de rebonds d'équipe (offensifs + défensifs)
        """
        return self.offensive_rebounds + self.defensive_rebounds
    
    @property
    def field_goal_percentage(self):
        """
        Calcule le pourcentage de réussite aux tirs à 2 points de l'équipe
        
        Retourne:
        - Le pourcentage arrondi à une décimale si des tirs ont été tentés
        - None si aucun tir n'a été tenté
        """
        if self.field_goals_attempted == 0:
            return None
        return round((self.field_goals_made / self.field_goals_attempted) * 100, 1)
    
    @property
    def three_point_percentage(self):
        """
        Calcule le pourcentage de réussite aux tirs à 3 points de l'équipe
        
        Retourne:
        - Le pourcentage arrondi à une décimale si des tirs ont été tentés
        - None si aucun tir n'a été tenté
        """
        if self.three_pointers_attempted == 0:
            return None
        return round((self.three_pointers_made / self.three_pointers_attempted) * 100, 1)
    
    @property
    def free_throw_percentage(self):
        """
        Calcule le pourcentage de réussite aux lancers francs de l'équipe
        
        Retourne:
        - Le pourcentage arrondi à une décimale si des lancers ont été tentés
        - None si aucun lancer n'a été tenté
        """
        if self.free_throws_attempted == 0:
            return None
        return round((self.free_throws_made / self.free_throws_attempted) * 100, 1)
