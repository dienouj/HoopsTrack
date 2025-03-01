from rest_framework import permissions
from .models import User

class IsAdmin(permissions.BasePermission):
    """
    Permission permettant uniquement aux administrateurs d'accéder à certaines ressources.
    
    Cette permission vérifie si l'utilisateur connecté a le rôle 'ADMIN'.
    """
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur a un rôle administrateur.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            
        Returns:
            True si l'utilisateur est administrateur, False sinon
        """
        return request.user and request.user.role == User.ADMIN


class IsCoach(permissions.BasePermission):
    """
    Permission permettant uniquement aux coachs d'accéder à certaines ressources.
    
    Cette permission vérifie si l'utilisateur connecté a le rôle 'COACH'.
    """
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur a un rôle coach.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            
        Returns:
            True si l'utilisateur est coach, False sinon
        """
        return request.user and request.user.role == User.COACH


class IsPlayer(permissions.BasePermission):
    """
    Permission permettant uniquement aux joueurs d'accéder à certaines ressources.
    
    Cette permission vérifie si l'utilisateur connecté a le rôle 'PLAYER'.
    """
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur a un rôle joueur.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            
        Returns:
            True si l'utilisateur est joueur, False sinon
        """
        return request.user and request.user.role == User.PLAYER


class IsStatistician(permissions.BasePermission):
    """
    Permission permettant uniquement aux statisticiens d'accéder à certaines ressources.
    
    Cette permission vérifie si l'utilisateur connecté a le rôle 'STATISTICIAN'.
    """
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur a un rôle statisticien.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            
        Returns:
            True si l'utilisateur est statisticien, False sinon
        """
        return request.user and request.user.role == User.STATISTICIAN


class IsStaff(permissions.BasePermission):
    """
    Permission permettant uniquement au staff (coach ou statisticien) d'accéder à certaines ressources.
    
    Cette permission vérifie si l'utilisateur connecté a un rôle 'COACH' ou 'STATISTICIAN'.
    """
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur fait partie du staff.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            
        Returns:
            True si l'utilisateur est coach ou statisticien, False sinon
        """
        return request.user and request.user.role in [User.COACH, User.STATISTICIAN, User.ADMIN]


class IsTeamCoach(permissions.BasePermission):
    """
    Permission vérifiant si l'utilisateur est le coach de l'équipe concernée.
    
    Cette permission est utilisée au niveau de l'objet pour vérifier si l'utilisateur
    est le coach de l'équipe qu'il essaie de modifier.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est le coach de l'équipe.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            obj: L'objet (Team) sur lequel on effectue l'opération
            
        Returns:
            True si l'utilisateur est administrateur ou le coach de l'équipe, False sinon
        """
        return request.user and (
            request.user.role == User.ADMIN or 
            (request.user.role == User.COACH and hasattr(obj, 'coach') and obj.coach == request.user)
        )


class IsTeamStatistician(permissions.BasePermission):
    """
    Permission vérifiant si l'utilisateur est un statisticien de l'équipe concernée.
    
    Cette permission est utilisée au niveau de l'objet pour vérifier si l'utilisateur
    fait partie des statisticiens de l'équipe.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est statisticien de l'équipe.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            obj: L'objet (Team) sur lequel on effectue l'opération
            
        Returns:
            True si l'utilisateur est administrateur ou un statisticien de l'équipe, False sinon
        """
        return request.user and (
            request.user.role == User.ADMIN or 
            (request.user.role == User.STATISTICIAN and hasattr(obj, 'staff') and request.user in obj.staff.all())
        )


class IsTeamMember(permissions.BasePermission):
    """
    Permission vérifiant si l'utilisateur est membre de l'équipe concernée.
    
    Cette permission est utilisée au niveau de l'objet pour vérifier si l'utilisateur
    est joueur, coach ou statisticien de l'équipe.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est membre de l'équipe.
        
        Args:
            request: La requête HTTP
            view: La vue à laquelle on tente d'accéder
            obj: L'objet (Team) sur lequel on effectue l'opération
            
        Returns:
            True si l'utilisateur est administrateur, coach, statisticien ou joueur de l'équipe, False sinon
        """
        if not request.user:
            return False
        
        if request.user.role == User.ADMIN:
            return True
        
        # Cas où l'objet est une équipe
        if hasattr(obj, 'coach') and hasattr(obj, 'staff'):
            # Vérifier si coach
            if request.user.role == User.COACH and obj.coach == request.user:
                return True
                
            # Vérifier si statisticien
            if request.user.role == User.STATISTICIAN and request.user in obj.staff.all():
                return True
                
            # Vérifier si joueur de l'équipe
            if request.user.role == User.PLAYER:
                try:
                    player = request.user.player
                    if player.team == obj:
                        return True
                except:
                    pass
        
        return False
