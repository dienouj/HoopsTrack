from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Sum, Count, F
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Game, Performance, TeamPerformance
from teams.models import Team, Player

# Création des sérialiseurs pour les modèles de statistiques
from rest_framework import serializers

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
    # Inclusion des performances individuelles et d'équipe
    performances = PerformanceSerializer(many=True, read_only=True, source='performance_set')
    team_performances = TeamPerformanceSerializer(many=True, read_only=True, source='teamperformance_set')
    
    class Meta(GameSerializer.Meta):
        fields = GameSerializer.Meta.fields + ('performances', 'team_performances')

# Définition des ViewSets

class GameViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de consulter et d'éditer les matchs.
    
    Fournit des fonctionnalités CRUD complètes pour les matchs.
    Les détails d'un match incluent les performances individuelles et d'équipe.
    """
    queryset = Game.objects.all().order_by('-date')
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['home_team', 'away_team', 'status', 'season']
    search_fields = ['home_team__name', 'away_team__name', 'location', 'notes']
    ordering_fields = ['date', 'home_score', 'away_score']
    
    def get_serializer_class(self):
        """
        Utilise différents sérialiseurs selon l'action
        
        Returns:
            GameDetailSerializer pour l'action 'retrieve'
            GameSerializer pour toutes les autres actions
        """
        if self.action == 'retrieve':
            return GameDetailSerializer
        return GameSerializer
    
    def perform_create(self, serializer):
        """
        Associe l'utilisateur connecté comme créateur du match
        """
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def performances(self, request, pk=None):
        """
        Renvoie toutes les performances individuelles d'un match
        
        Returns:
            Un objet Response contenant les performances individuelles du match
        """
        game = self.get_object()
        performances = Performance.objects.filter(game=game)
        serializer = PerformanceSerializer(performances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def team_performances(self, request, pk=None):
        """
        Renvoie les performances d'équipe d'un match
        
        Returns:
            Un objet Response contenant les performances d'équipe du match
        """
        game = self.get_object()
        team_performances = TeamPerformance.objects.filter(game=game)
        serializer = TeamPerformanceSerializer(team_performances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_team(self, request):
        """
        Filtre les matchs par équipe
        
        Returns:
            Un objet Response contenant les matchs de l'équipe spécifiée
        """
        team_id = request.query_params.get('team_id', None)
        if team_id is None:
            return Response(
                {"detail": "Le paramètre team_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Matchs où l'équipe joue à domicile ou à l'extérieur
        games = self.queryset.filter(
            models.Q(home_team_id=team_id) | models.Q(away_team_id=team_id)
        )
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

class PerformanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de consulter et d'éditer les performances individuelles.
    
    Fournit des fonctionnalités CRUD complètes pour les performances des joueurs.
    """
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['player', 'game', 'game__home_team', 'game__away_team']
    search_fields = ['player__user__first_name', 'player__user__last_name', 'notes']
    ordering_fields = ['points', 'rebounds', 'assists', 'steals', 'blocks']
    
    def perform_create(self, serializer):
        """
        Associe l'utilisateur connecté comme créateur de la performance
        """
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_player(self, request):
        """
        Récupère toutes les performances d'un joueur spécifique
        
        Returns:
            Un objet Response contenant les performances du joueur spécifié
        """
        player_id = request.query_params.get('player_id', None)
        if player_id is None:
            return Response(
                {"detail": "Le paramètre player_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        performances = self.queryset.filter(player_id=player_id).order_by('-game__date')
        serializer = self.get_serializer(performances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def player_averages(self, request):
        """
        Calcule les statistiques moyennes d'un joueur
        
        Returns:
            Un objet Response contenant les moyennes statistiques du joueur
        """
        player_id = request.query_params.get('player_id', None)
        if player_id is None:
            return Response(
                {"detail": "Le paramètre player_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        player = get_object_or_404(Player, pk=player_id)
        stats = Performance.objects.filter(player=player).aggregate(
            games=Count('id'),
            ppg=Avg('points'),
            rpg=Avg('total_rebounds'),
            apg=Avg('assists'),
            spg=Avg('steals'),
            bpg=Avg('blocks'),
            fg_pct=Avg('field_goal_percentage'),
            three_pct=Avg('three_point_percentage'),
            ft_pct=Avg('free_throw_percentage')
        )
        
        # Ajout des informations du joueur
        if player.user:
            stats['player_name'] = f"{player.user.first_name} {player.user.last_name}"
        else:
            stats['player_name'] = "Joueur inconnu"
        stats['jersey_number'] = player.jersey_number
        stats['position'] = player.position
        
        return Response(stats)

class TeamPerformanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de consulter et d'éditer les performances d'équipe.
    
    Fournit des fonctionnalités CRUD complètes pour les performances collectives.
    """
    queryset = TeamPerformance.objects.all()
    serializer_class = TeamPerformanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team', 'game']
    search_fields = ['team__name']
    ordering_fields = ['points', 'rebounds', 'assists']
    
    def perform_create(self, serializer):
        """
        Associe l'utilisateur connecté comme créateur de la performance d'équipe
        """
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def team_averages(self, request):
        """
        Calcule les statistiques moyennes d'une équipe
        
        Returns:
            Un objet Response contenant les moyennes statistiques de l'équipe
        """
        team_id = request.query_params.get('team_id', None)
        if team_id is None:
            return Response(
                {"detail": "Le paramètre team_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        team = get_object_or_404(Team, pk=team_id)
        stats = TeamPerformance.objects.filter(team=team).aggregate(
            games=Count('id'),
            ppg=Avg('points'),
            rpg=Avg('total_rebounds'),
            apg=Avg('assists'),
            spg=Avg('steals'),
            bpg=Avg('blocks'),
            fg_pct=Avg('field_goal_percentage'),
            three_pct=Avg('three_point_percentage'),
            ft_pct=Avg('free_throw_percentage')
        )
        
        # Ajout des informations de l'équipe
        stats['team_name'] = team.name
        stats['team_city'] = team.city
        
        # Calcul du bilan victoires/défaites
        from django.db.models import Q, Case, When, IntegerField
        
        # Matchs à domicile
        home_games = Game.objects.filter(home_team=team)
        home_wins = home_games.filter(home_score__gt=F('away_score')).count()
        
        # Matchs à l'extérieur
        away_games = Game.objects.filter(away_team=team)
        away_wins = away_games.filter(away_score__gt=F('home_score')).count()
        
        total_games = home_games.count() + away_games.count()
        total_wins = home_wins + away_wins
        
        stats['wins'] = total_wins
        stats['losses'] = total_games - total_wins
        stats['win_percentage'] = round(total_wins / total_games, 3) if total_games > 0 else 0
        
        return Response(stats)
