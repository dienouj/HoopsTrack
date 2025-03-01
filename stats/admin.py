from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Game, Performance, TeamPerformance

# Register your models here.

class PerformanceInline(admin.TabularInline):
    """
    Configuration d'affichage en ligne des performances individuelles dans l'interface d'administration des matchs
    
    Permet d'ajouter et de modifier les performances des joueurs directement depuis la page 
    d'administration d'un match, sans avoir à naviguer vers une page distincte.
    """
    model = Performance  # Modèle à afficher en ligne
    extra = 0  # Nombre de formulaires vides à afficher (0 = aucun formulaire vide par défaut)
    fields = ('player', 'minutes_played', 'points', 'rebounds', 'assists', 'steals', 'blocks')
    readonly_fields = ('rebounds',)  # Champ calculé, non modifiable directement
    
    def rebounds(self, obj):
        """
        Méthode calculée pour afficher le total des rebonds
        
        Args:
            obj: L'instance de Performance
            
        Returns:
            Nombre total de rebonds ou "-" si l'objet n'existe pas encore
        """
        if obj.pk:  # Si l'objet existe déjà en base de données
            return obj.total_rebounds
        return "-"
    rebounds.short_description = _('Rebounds')  # Libellé de l'en-tête de colonne

class TeamPerformanceInline(admin.TabularInline):
    """
    Configuration d'affichage en ligne des performances d'équipe dans l'interface d'administration des matchs
    
    Permet d'ajouter et de modifier les performances globales des équipes directement depuis la page
    d'administration d'un match. Limité à 2 équipes maximum (équipe à domicile et équipe à l'extérieur).
    """
    model = TeamPerformance  # Modèle à afficher en ligne
    extra = 0  # Nombre de formulaires vides à afficher
    max_num = 2  # Nombre maximum d'instances (limité à 2 équipes par match)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Game (Match)
    
    Cette classe définit comment les matchs sont affichés et gérés
    dans l'interface d'administration Django. Les administrateurs peuvent:
    - Voir la liste des matchs avec date, lieu, statut et scores
    - Filtrer les matchs par statut, date ou équipes
    - Rechercher des matchs par nom d'équipe ou lieu
    - Visualiser et gérer les performances individuelles et d'équipe via des inlines
    """
    # Configuration de l'affichage dans la liste des matchs
    list_display = (
        '__str__',     # Représentation string du match (généralement équipes en confrontation)
        'date',        # Date du match
        'location',    # Lieu du match 
        'status',      # Statut du match (planifié, en cours, terminé)
        'home_score',  # Score de l'équipe à domicile
        'away_score'   # Score de l'équipe à l'extérieur
    )
    
    # Filtres disponibles dans la barre latérale
    list_filter = (
        'status',     # Filtrer par statut du match
        'date',       # Filtrer par date
        'home_team',  # Filtrer par équipe à domicile
        'away_team'   # Filtrer par équipe à l'extérieur
    )
    
    # Champs utilisés pour la recherche de matchs
    search_fields = (
        'home_team__name',  # Nom de l'équipe à domicile
        'away_team__name',  # Nom de l'équipe à l'extérieur
        'location'          # Lieu du match
    )
    
    # Navigation hiérarchique par date
    date_hierarchy = 'date'
    
    # Modèles à afficher en ligne dans le formulaire d'édition du match
    inlines = [PerformanceInline, TeamPerformanceInline]

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Performance (Statistiques individuelles)
    
    Cette classe définit comment les performances individuelles sont affichées et gérées
    dans l'interface d'administration Django. Les administrateurs peuvent:
    - Voir la liste des performances avec les statistiques principales
    - Filtrer par date de match, équipe ou joueur
    - Rechercher des performances par nom de joueur ou d'équipe
    - Editer les performances avec une interface organisée par catégories de statistiques
    """
    # Configuration de l'affichage dans la liste des performances
    list_display = (
        'player',        # Joueur concerné
        'game',          # Match concerné
        'points',        # Points marqués
        'total_rebounds', # Total des rebonds
        'assists',       # Passes décisives
        'steals',        # Interceptions
        'blocks'         # Contres
    )
    
    # Filtres disponibles dans la barre latérale
    list_filter = (
        'game__date',    # Filtrer par date du match
        'player__team',  # Filtrer par équipe du joueur
        'player'         # Filtrer par joueur
    )
    
    # Champs utilisés pour la recherche de performances
    search_fields = (
        'player__user__first_name',    # Prénom du joueur
        'player__user__last_name',     # Nom du joueur
        'game__home_team__name',       # Nom de l'équipe à domicile
        'game__away_team__name'        # Nom de l'équipe à l'extérieur
    )
    
    # Navigation hiérarchique par date de match
    date_hierarchy = 'game__date'
    
    # Champs calculés automatiquement, non modifiables directement
    readonly_fields = (
        'field_goal_percentage',    # % de réussite aux tirs
        'three_point_percentage',   # % de réussite aux 3 points
        'free_throw_percentage',    # % de réussite aux lancers francs
        'total_rebounds'            # Total des rebonds (offensifs + défensifs)
    )
    
    # Organisation des champs par sections dans le formulaire d'édition
    fieldsets = (
        # Section de base - informations principales
        (None, {
            'fields': ('player', 'game', 'minutes_played')
        }),
        # Section scoring - statistiques offensives
        (_('Scoring'), {
            'fields': (
                'points',  # Points totaux
                # Tirs à 2 points - réussis, tentés et pourcentage
                ('field_goals_made', 'field_goals_attempted', 'field_goal_percentage'),
                # Tirs à 3 points - réussis, tentés et pourcentage
                ('three_pointers_made', 'three_pointers_attempted', 'three_point_percentage'),
                # Lancers francs - réussis, tentés et pourcentage
                ('free_throws_made', 'free_throws_attempted', 'free_throw_percentage'),
            )
        }),
        # Section autres statistiques - rebonds, passes, etc.
        (_('Other Stats'), {
            'fields': (
                # Rebonds offensifs, défensifs et total
                ('offensive_rebounds', 'defensive_rebounds', 'total_rebounds'),
                'assists',        # Passes décisives
                'steals',         # Interceptions
                'blocks',         # Contres
                'turnovers',      # Pertes de balle
                'personal_fouls', # Fautes personnelles
                'notes',          # Notes d'observation
            )
        }),
        # Section métadonnées - informations de création et modification
        (_('Meta'), {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    # Utilise un widget de recherche avancé pour les relations clés
    raw_id_fields = ('player', 'game', 'created_by')
    
    def get_readonly_fields(self, request, obj=None):
        """
        Détermine dynamiquement quels champs doivent être en lecture seule
        
        Les dates de création et modification sont automatiquement en lecture seule
        lors de l'édition d'un objet existant.
        
        Args:
            request: La requête HTTP courante
            obj: L'instance de Performance (None si création)
            
        Returns:
            Liste des champs en lecture seule
        """
        readonly_fields = list(self.readonly_fields)
        if obj:  # Edition d'un objet existant
            readonly_fields.extend(['created_at', 'updated_at'])
        return readonly_fields

@admin.register(TeamPerformance)
class TeamPerformanceAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle TeamPerformance (Performances d'équipe)
    
    Cette classe définit comment les performances globales d'équipe sont affichées et gérées
    dans l'interface d'administration Django. Les administrateurs peuvent:
    - Voir la liste des performances d'équipe avec les statistiques principales
    - Filtrer par date de match ou équipe
    - Rechercher des performances par nom d'équipe
    """
    # Configuration de l'affichage dans la liste des performances d'équipe
    list_display = (
        'team',          # Équipe concernée
        'game',          # Match concerné
        'points',        # Points marqués
        'total_rebounds', # Total des rebonds
        'assists',       # Passes décisives
        'steals',        # Interceptions
        'blocks'         # Contres
    )
    
    # Filtres disponibles dans la barre latérale
    list_filter = (
        'game__date',  # Filtrer par date du match
        'team'         # Filtrer par équipe
    )
    
    # Champs utilisés pour la recherche de performances d'équipe
    search_fields = (
        'team__name',            # Nom de l'équipe
        'game__home_team__name', # Nom de l'équipe à domicile
        'game__away_team__name'  # Nom de l'équipe à l'extérieur
    )
    
    # Navigation hiérarchique par date de match
    date_hierarchy = 'game__date'
    
    # Champs calculés automatiquement, non modifiables directement
    readonly_fields = (
        'field_goal_percentage',  # % de réussite aux tirs
        'three_point_percentage', # % de réussite aux 3 points
        'free_throw_percentage',  # % de réussite aux lancers francs
        'total_rebounds'          # Total des rebonds (offensifs + défensifs)
    )
    
    # Utilise un widget de recherche avancé pour les relations clés
    raw_id_fields = ('team', 'game', 'created_by')
