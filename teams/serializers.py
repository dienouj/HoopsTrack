from rest_framework import serializers
from .models import Team, Player
from users.models import User

class PlayerSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Player
    
    Inclut les informations de base du joueur ainsi que les données utilisateur associées.
    """
    # Inclusion des informations de l'utilisateur associé au joueur
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Player
        fields = ('id', 'user', 'user_first_name', 'user_last_name', 'user_email',
                 'team', 'jersey_number', 'position', 'height', 'weight', 
                 'active', 'birth_date')
        read_only_fields = ('user_first_name', 'user_last_name', 'user_email')


class TeamSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Team
    
    Inclut les informations de base de l'équipe ainsi que les joueurs associés.
    """
    # Ajout d'un champ calculé pour le nombre de joueurs
    player_count = serializers.SerializerMethodField()
    coach_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Team
        fields = ('id', 'name', 'logo', 'city', 'description', 'coach',
                 'coach_name', 'staff', 'player_count')
        read_only_fields = ('coach_name', 'player_count')
    
    def get_player_count(self, obj):
        """
        Calcule le nombre de joueurs dans l'équipe
        
        Args:
            obj: L'instance Team
            
        Returns:
            Le nombre de joueurs actifs dans l'équipe
        """
        return obj.player_set.filter(active=True).count()
    
    def get_coach_name(self, obj):
        """
        Récupère le nom du coach
        
        Args:
            obj: L'instance Team
            
        Returns:
            Le nom complet du coach ou une chaîne vide
        """
        if obj.coach:
            return f"{obj.coach.first_name} {obj.coach.last_name}"
        return ""


class TeamDetailSerializer(TeamSerializer):
    """
    Sérialiseur pour les détails d'une équipe, incluant la liste des joueurs
    """
    players = PlayerSerializer(many=True, read_only=True, source='player_set')
    
    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ('players',)
