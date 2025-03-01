from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Team, Player
from users.models import User

# Création des sérialiseurs pour les modèles Team et Player
from rest_framework import serializers

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
    
    class Meta:
        model = Team
        fields = ('id', 'name', 'logo', 'city', 'description', 'coach',
                 'staff', 'player_count')
    
    def get_player_count(self, obj):
        """
        Calcule le nombre de joueurs dans l'équipe
        
        Args:
            obj: L'instance Team
            
        Returns:
            Le nombre de joueurs associés à cette équipe
        """
        return obj.players.count()

class TeamDetailSerializer(TeamSerializer):
    """
    Sérialiseur pour les détails d'une équipe, incluant la liste des joueurs
    """
    # Inclusion de la liste détaillée des joueurs
    players = PlayerSerializer(many=True, read_only=True)
    
    class Meta(TeamSerializer.Meta):
        # Ajout du champ 'players' à la liste des champs
        fields = TeamSerializer.Meta.fields + ('players',)

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
    
    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        """
        Renvoie la liste des joueurs pour une équipe spécifique
        
        Returns:
            Un objet Response contenant la liste des joueurs de l'équipe
        """
        team = self.get_object()
        players = team.players.all()
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def active_players(self, request, pk=None):
        """
        Renvoie uniquement les joueurs actifs d'une équipe
        
        Returns:
            Un objet Response contenant la liste des joueurs actifs de l'équipe
        """
        team = self.get_object()
        players = team.players.filter(active=True)
        serializer = PlayerSerializer(players, many=True)
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
    
    @action(detail=False, methods=['get'])
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
                {"detail": "L'utilisateur connecté n'a pas de profil joueur associé."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
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
        
        players = self.queryset.filter(team_id=team_id)
        serializer = self.get_serializer(players, many=True)
        return Response(serializer.data)
