from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# Récupérer le modèle utilisateur personnalisé défini dans settings.AUTH_USER_MODEL
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle User - Utilisé pour l'affichage et la mise à jour des informations utilisateur
    
    Ce sérialiseur expose les informations de base de l'utilisateur tout en masquant
    les informations sensibles comme le mot de passe. Il est utilisé pour:
    - Afficher les détails d'un utilisateur
    - Mettre à jour les informations d'un utilisateur existant
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role',
                 'phone', 'bio', 'profile_picture', 'date_joined')
        read_only_fields = ('date_joined',)  # Ce champ ne peut pas être modifié via l'API


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création de nouveaux comptes utilisateur
    
    Ce sérialiseur gère spécifiquement la création de nouveaux utilisateurs avec:
    - Validation du mot de passe selon les règles de sécurité Django
    - Confirmation du mot de passe pour éviter les erreurs de saisie
    - Création sécurisée du compte utilisateur avec hachage du mot de passe
    """
    # Champ pour le mot de passe avec validation
    password = serializers.CharField(
        write_only=True,  # Le mot de passe ne sera jamais renvoyé dans les réponses API
        required=True,
        validators=[validate_password]  # Utilise les validateurs de mot de passe configurés dans Django
    )
    
    # Champ pour la confirmation du mot de passe
    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'role', 'phone', 'bio')
    
    def validate(self, data):
        """
        Validation personnalisée pour s'assurer que les deux mots de passe correspondent
        
        Args:
            data: Les données soumises au sérialiseur
            
        Returns:
            Les données validées
            
        Raises:
            ValidationError: Si les mots de passe ne correspondent pas
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    def create(self, validated_data):
        """
        Crée un nouvel utilisateur avec les données validées
        
        Cette méthode:
        1. Supprime le champ de confirmation du mot de passe
        2. Utilise create_user() qui s'assure du hachage sécurisé du mot de passe
        
        Args:
            validated_data: Les données validées par le sérialiseur
            
        Returns:
            L'instance User nouvellement créée
        """
        # Supprimer le champ de confirmation du mot de passe avant création
        validated_data.pop('password_confirm')
        
        # Utiliser create_user pour un hachage sécurisé du mot de passe
        user = User.objects.create_user(**validated_data)
        return user
