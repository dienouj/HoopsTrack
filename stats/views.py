from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Sum, Count, F
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Game, Performance, TeamPerformance
from teams.models import Team, Player
from .serializers import GameSerializer, GameDetailSerializer, PerformanceSerializer, TeamPerformanceSerializer

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
    
    @action(detail=True, methods=['get'], url_path='performances')
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
    
    @action(detail=True, methods=['get'], url_path='team-performances')
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
    
    @action(detail=False, methods=['get'], url_path='by-team')
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
        
        games = Game.objects.filter(home_team_id=team_id) | Game.objects.filter(away_team_id=team_id)
        games = games.order_by('-date')
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
    
    @action(detail=False, methods=['get'], url_path='by-player')
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
        
        performances = Performance.objects.filter(player_id=player_id).order_by('-game__date')
        serializer = self.get_serializer(performances, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='player-averages')
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
        
        # Vérifier que le joueur existe
        player = get_object_or_404(Player, pk=player_id)
        
        # Calculer les moyennes des performances du joueur
        averages = Performance.objects.filter(player_id=player_id).aggregate(
            avg_points=Avg('points'),
            avg_rebounds=Avg('total_rebounds'),
            avg_assists=Avg('assists'),
            avg_steals=Avg('steals'),
            avg_blocks=Avg('blocks'),
            avg_turnovers=Avg('turnovers'),
            avg_minutes=Avg('minutes_played'),
            avg_field_goal_pct=Avg('field_goal_percentage'),
            avg_three_point_pct=Avg('three_point_percentage'),
            avg_free_throw_pct=Avg('free_throw_percentage'),
            games_played=Count('id')
        )
        
        # Ajouter les informations du joueur aux statistiques
        player_info = {
            'player_id': player.id,
            'player_name': f"{player.user.first_name} {player.user.last_name}",
            'team': player.team.name if player.team else None,
            'jersey_number': player.jersey_number,
            'position': player.position
        }
        
        response_data = {**player_info, **averages}
        return Response(response_data)


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
    
    @action(detail=False, methods=['get'], url_path='team-averages')
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
        
        # Vérifier que l'équipe existe
        team = get_object_or_404(Team, pk=team_id)
        
        # Calculer les moyennes des performances de l'équipe
        averages = TeamPerformance.objects.filter(team_id=team_id).aggregate(
            avg_points=Avg('points'),
            avg_rebounds=Avg('total_rebounds'),
            avg_assists=Avg('assists'),
            avg_steals=Avg('steals'),
            avg_blocks=Avg('blocks'),
            avg_turnovers=Avg('turnovers'),
            avg_field_goal_pct=Avg('field_goal_percentage'),
            avg_three_point_pct=Avg('three_point_percentage'),
            avg_free_throw_pct=Avg('free_throw_percentage'),
            games_played=Count('id')
        )
        
        # Ajouter les informations de l'équipe aux statistiques
        team_info = {
            'team_id': team.id,
            'team_name': team.name,
            'city': team.city
        }
        
        response_data = {**team_info, **averages}
        return Response(response_data)
