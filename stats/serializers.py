from rest_framework import serializers
from .models import Game, Performance, TeamPerformance
from teams.models import Team, Player

class PerformanceSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Performance (statistiques individuelles)
    
    Inclut les statistiques complètes d'un joueur pour un match donné.
    """
    # Informations sur le joueur et le match
    player_name = serializers.SerializerMethodField()
    game_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Performance
        fields = ('id', 'player', 'player_name', 'game', 'game_info', 'minutes_played',
                 'points', 'field_goals_made', 'field_goals_attempted', 'field_goal_percentage',
                 'three_pointers_made', 'three_pointers_attempted', 'three_point_percentage',
                 'free_throws_made', 'free_throws_attempted', 'free_throw_percentage',
                 'offensive_rebounds', 'defensive_rebounds', 'total_rebounds',
                 'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls', 'notes',
                 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('field_goal_percentage', 'three_point_percentage', 
                           'free_throw_percentage', 'total_rebounds',
                           'created_at', 'updated_at')
    
    def get_player_name(self, obj):
        """
        Obtient le nom complet du joueur
        """
        if obj.player and obj.player.user:
            return f"{obj.player.user.first_name} {obj.player.user.last_name}"
        return "Joueur inconnu"
    
    def get_game_info(self, obj):
        """
        Obtient les informations du match (équipes en confrontation)
        """
        if obj.game:
            return f"{obj.game.home_team.name} vs {obj.game.away_team.name} ({obj.game.date})"
        return "Match inconnu"


class TeamPerformanceSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle TeamPerformance (statistiques d'équipe)
    
    Inclut les statistiques collectives d'une équipe pour un match donné.
    """
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = TeamPerformance
        fields = ('id', 'team', 'team_name', 'game', 'points',
                 'field_goals_made', 'field_goals_attempted', 'field_goal_percentage',
                 'three_pointers_made', 'three_pointers_attempted', 'three_point_percentage',
                 'free_throws_made', 'free_throws_attempted', 'free_throw_percentage',
                 'offensive_rebounds', 'defensive_rebounds', 'total_rebounds',
                 'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls',
                 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('field_goal_percentage', 'three_point_percentage', 
                           'free_throw_percentage', 'total_rebounds',
                           'created_at', 'updated_at')


class GameSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Game (match)
    
    Inclut les informations de base sur un match.
    """
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    
    class Meta:
        model = Game
        fields = ('id', 'home_team', 'home_team_name', 'away_team', 'away_team_name',
                 'date', 'location', 'status', 'home_score', 'away_score', 'season',
                 'notes', 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class GameDetailSerializer(GameSerializer):
    """
    Sérialiseur pour les détails d'un match, incluant les performances
    """
    performances = PerformanceSerializer(many=True, read_only=True, source='performance_set')
    team_performances = TeamPerformanceSerializer(many=True, read_only=True, source='teamperformance_set')
    
    class Meta(GameSerializer.Meta):
        fields = GameSerializer.Meta.fields + ('performances', 'team_performances')
