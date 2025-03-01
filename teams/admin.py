from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Team, Player

# Register your models here.

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Team (Équipe)
    
    Cette classe définit comment les équipes sont affichées et gérées
    dans l'interface d'administration Django. Les administrateurs peuvent:
    - Voir la liste des équipes avec leur nom, ville, coach et nombre de joueurs
    - Rechercher des équipes par nom ou ville
    - Ajouter/Supprimer facilement des membres du staff via une interface horizontale
    """
    # Configuration de l'affichage dans la liste des équipes
    list_display = (
        'name',          # Nom de l'équipe
        'city',          # Ville de l'équipe
        'coach',         # Coach responsable (lien vers un utilisateur)
        'get_player_count' # Nombre de joueurs (méthode calculée)
    )
    
    # Champs utilisés pour la recherche d'équipes
    search_fields = ('name', 'city')
    
    # Interface améliorée pour sélectionner plusieurs membres du staff
    filter_horizontal = ('staff',)
    
    def get_player_count(self, obj):
        """
        Calcule et renvoie le nombre de joueurs dans l'équipe
        
        Args:
            obj: L'instance de l'équipe
            
        Returns:
            Nombre entier de joueurs associés à cette équipe
        """
        return obj.players.count()
    # Nom personnalisé affiché dans l'en-tête de colonne
    get_player_count.short_description = _('Players')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Player (Joueur)
    
    Cette classe définit comment les joueurs sont affichés et gérés
    dans l'interface d'administration Django. Les administrateurs peuvent:
    - Voir la liste des joueurs avec leurs informations clés
    - Filtrer les joueurs par équipe, position et statut d'activité
    - Rechercher des joueurs par nom ou numéro de maillot
    - Sélectionner l'utilisateur et l'équipe associés via une interface de recherche optimisée
    """
    # Configuration de l'affichage dans la liste des joueurs
    list_display = (
        '__str__',      # Représentation string du joueur (généralement nom + prénom)
        'team',         # Équipe associée
        'jersey_number', # Numéro de maillot 
        'position',     # Poste de jeu (PG, SG, SF, etc.)
        'height',       # Taille du joueur
        'weight',       # Poids du joueur
        'active'        # Statut d'activité du joueur
    )
    
    # Filtres disponibles dans la barre latérale
    list_filter = (
        'team',         # Filtrer par équipe
        'position',     # Filtrer par poste de jeu
        'active'        # Filtrer par statut d'activité
    )
    
    # Champs utilisés pour la recherche de joueurs
    search_fields = (
        'user__first_name',  # Prénom de l'utilisateur associé
        'user__last_name',   # Nom de l'utilisateur associé
        'jersey_number'      # Numéro de maillot
    )
    
    # Utilise un widget de recherche avancé pour les relations clés
    raw_id_fields = (
        'user',  # Lien vers le modèle utilisateur
        'team'   # Lien vers le modèle équipe
    )
