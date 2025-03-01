from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.hashers import make_password

from .models import User
from .serializers import UserSerializer
from .permissions import IsAdmin, IsCoach, IsStatistician, IsPlayer, IsStaff

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour la gestion des utilisateurs.
    
    Permet d'ajouter, de consulter, de modifier et de supprimer des utilisateurs.
    Seuls les administrateurs ont un accès complet. Les autres utilisateurs ont
    des permissions restreintes en fonction de leur rôle.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username', 'first_name', 'last_name', 'role']
    
    def get_permissions(self):
        """
        Définit les permissions en fonction de l'action demandée.
        
        - create, update, partial_update, destroy: admin uniquement
        - list: admin, coach ou statisticien
        - retrieve: tous les utilisateurs authentifiés
        - autres actions personnalisées: leurs permissions spécifiques
        
        Returns:
            Liste des permissions applicables pour cette action
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        elif self.action == 'list':
            permission_classes = [IsStaff]
        elif self.action in ['me', 'update_me']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Surcharge de la méthode de création pour hasher le mot de passe.
        
        Args:
            serializer: Le sérialiseur contenant les données validées
        """
        password = serializer.validated_data.get('password', None)
        if password:
            serializer.validated_data['password'] = make_password(password)
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Surcharge de la méthode de mise à jour pour hasher le mot de passe si fourni.
        
        Args:
            serializer: Le sérialiseur contenant les données validées
        """
        password = serializer.validated_data.get('password', None)
        if password:
            serializer.validated_data['password'] = make_password(password)
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Renvoie les informations de l'utilisateur actuellement connecté.
        
        Returns:
            Un objet Response contenant les informations de l'utilisateur connecté
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """
        Permet à l'utilisateur connecté de mettre à jour ses propres informations.
        
        Seules certaines informations peuvent être modifiées par l'utilisateur lui-même.
        
        Args:
            request: La requête HTTP contenant les données à mettre à jour
            
        Returns:
            Un objet Response contenant les informations de l'utilisateur mises à jour
        """
        user = request.user
        
        # Liste des champs autorisés à la modification par l'utilisateur lui-même
        allowed_fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        
        # Filtrer les données pour ne garder que les champs autorisés
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        # Si le mot de passe est fourni, le hasher
        if 'password' in update_data:
            update_data['password'] = make_password(update_data['password'])
        
        # Mettre à jour l'utilisateur
        for key, value in update_data.items():
            setattr(user, key, value)
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def coaches(self, request):
        """
        Liste tous les coachs.
        
        Returns:
            Un objet Response contenant la liste des coachs
        """
        coaches = User.objects.filter(role=User.COACH)
        serializer = self.get_serializer(coaches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def players(self, request):
        """
        Liste tous les joueurs.
        
        Returns:
            Un objet Response contenant la liste des joueurs
        """
        players = User.objects.filter(role=User.PLAYER)
        serializer = self.get_serializer(players, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statisticians(self, request):
        """
        Liste tous les statisticiens.
        
        Returns:
            Un objet Response contenant la liste des statisticiens
        """
        statisticians = User.objects.filter(role=User.STATISTICIAN)
        serializer = self.get_serializer(statisticians, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def is_coach(self, request, pk=None):
        """
        Vérifie si l'utilisateur est un coach.
        
        Returns:
            Un objet Response indiquant si l'utilisateur est un coach
        """
        user = self.get_object()
        return Response({
            'is_coach': user.role == User.COACH
        })
    
    @action(detail=True, methods=['get'])
    def is_player(self, request, pk=None):
        """
        Vérifie si l'utilisateur est un joueur.
        
        Returns:
            Un objet Response indiquant si l'utilisateur est un joueur
        """
        user = self.get_object()
        return Response({
            'is_player': user.role == User.PLAYER
        })
    
    @action(detail=True, methods=['get'])
    def is_statistician(self, request, pk=None):
        """
        Vérifie si l'utilisateur est un statisticien.
        
        Returns:
            Un objet Response indiquant si l'utilisateur est un statisticien
        """
        user = self.get_object()
        return Response({
            'is_statistician': user.role == User.STATISTICIAN
        })
