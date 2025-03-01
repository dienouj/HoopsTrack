from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint qui permet de consulter et d'éditer les utilisateurs.
    
    Fournit des fonctionnalités CRUD complètes pour les utilisateurs.
    L'accès est restreint en fonction du rôle et des permissions de l'utilisateur.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Retourne le sérialiseur approprié en fonction de l'action.
        
        Returns:
            Le sérialiseur UserCreateSerializer pour les actions de création,
            UserSerializer pour toutes les autres actions.
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Définit les permissions en fonction de l'action.
        
        Returns:
            Permissions AllowAny pour l'inscription (create),
            IsAuthenticated pour toutes les autres actions.
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Renvoie les informations de l'utilisateur actuellement connecté.
        
        Cette endpoint est utile pour que les clients puissent récupérer
        les informations de l'utilisateur connecté sans connaître son ID.
        
        Returns:
            Un objet Response contenant les données sérialisées de l'utilisateur courant.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='is-coach')
    def is_coach(self, request, pk=None):
        """
        Vérifie si l'utilisateur spécifié a le rôle de coach.
        
        Returns:
            Un objet Response indiquant si l'utilisateur est coach ou non.
        """
        user = self.get_object()
        return Response({'is_coach': user.role == 'COACH'})
    
    @action(detail=True, methods=['get'], url_path='is-player')
    def is_player(self, request, pk=None):
        """
        Vérifie si l'utilisateur spécifié a le rôle de joueur.
        
        Returns:
            Un objet Response indiquant si l'utilisateur est joueur ou non.
        """
        user = self.get_object()
        return Response({'is_player': user.role == 'PLAYER'})
    
    @action(detail=True, methods=['get'], url_path='is-statistician')
    def is_statistician(self, request, pk=None):
        """
        Vérifie si l'utilisateur spécifié a le rôle de statisticien.
        
        Returns:
            Un objet Response indiquant si l'utilisateur est statisticien ou non.
        """
        user = self.get_object()
        return Response({'is_statistician': user.role == 'STATISTICIAN'})
