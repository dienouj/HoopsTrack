from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Team, Player
from users.models import User
from .serializers import PlayerSerializer, TeamSerializer, TeamDetailSerializer

# Définition des ViewSets

class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de consulter et d'éditer les équipes.
    
    Fournit des fonctionnalités CRUD complètes pour les équipes.
    Les détails d'une équipe incluent la liste des joueurs associés.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'coach']
    search_fields = ['name', 'city', 'description']
    ordering_fields = ['name', 'city']
    
    def get_serializer_class(self):
        """
        Utilise différents sérialiseurs selon l'action
        
        Returns:
            TeamDetailSerializer pour l'action 'retrieve'
            TeamSerializer pour toutes les autres actions
        """
        if self.action == 'retrieve':
            return TeamDetailSerializer
        return TeamSerializer
    
    @action(detail=True, methods=['get'], url_path='players')
    def players(self, request, pk=None):
        """
        Renvoie la liste des joueurs pour une équipe spécifique
        
        Returns:
            Un objet Response contenant la liste des joueurs de l'équipe
        """
        team = self.get_object()
        players = Player.objects.filter(team=team)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='active-players')
    def active_players(self, request, pk=None):
        """
        Renvoie uniquement les joueurs actifs d'une équipe
        
        Returns:
            Un objet Response contenant la liste des joueurs actifs de l'équipe
        """
        team = self.get_object()
        active_players = Player.objects.filter(team=team, active=True)
        serializer = PlayerSerializer(active_players, many=True)
        return Response(serializer.data)
    

class PlayerViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de consulter et d'éditer les joueurs.
    
    Fournit des fonctionnalités CRUD complètes pour les joueurs.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team', 'position', 'active']
    search_fields = ['user__first_name', 'user__last_name', 'jersey_number']
    ordering_fields = ['jersey_number', 'height', 'weight']
    
    @action(detail=False, methods=['get'], url_path='me')
    def by_user(self, request):
        """
        Récupère le profil joueur de l'utilisateur connecté
        
        Returns:
            Le profil du joueur associé à l'utilisateur connecté, ou 404 si non trouvé
        """
        try:
            player = Player.objects.get(user=request.user)
            serializer = self.get_serializer(player)
            return Response(serializer.data)
        except Player.DoesNotExist:
            return Response(
                {"detail": "Aucun profil de joueur trouvé pour cet utilisateur."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='by-team')
    def by_team(self, request):
        """
        Filtre les joueurs par équipe via un paramètre de requête
        
        Returns:
            Liste des joueurs de l'équipe spécifiée, ou une erreur si le paramètre est manquant
        """
        team_id = request.query_params.get('team_id', None)
        if team_id is None:
            return Response(
                {"detail": "Le paramètre team_id est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        players = Player.objects.filter(team_id=team_id)
        serializer = self.get_serializer(players, many=True)
        return Response(serializer.data)
