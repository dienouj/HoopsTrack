from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User
from .serializers import UserSerializer

class UserModelTests(TestCase):
    """
    Tests pour le modèle User
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests
        """
        self.user_admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='securepassword123',
            first_name='Admin',
            last_name='User',
            role=User.ADMIN
        )
        
        self.user_coach = User.objects.create_user(
            username='coach_test',
            email='coach@test.com',
            password='securepassword123',
            first_name='Coach',
            last_name='User',
            role=User.COACH
        )
        
        self.user_player = User.objects.create_user(
            username='player_test',
            email='player@test.com',
            password='securepassword123',
            first_name='Player',
            last_name='User',
            role=User.PLAYER
        )
        
        self.user_statistician = User.objects.create_user(
            username='stat_test',
            email='statistician@test.com',
            password='securepassword123',
            first_name='Stat',
            last_name='User',
            role=User.STATISTICIAN
        )
    
    def test_user_creation(self):
        """
        Teste la création d'utilisateurs avec différents rôles
        """
        self.assertEqual(self.user_admin.username, 'admin_test')
        self.assertEqual(self.user_coach.role, User.COACH)
        self.assertEqual(self.user_player.role, User.PLAYER)
        self.assertEqual(self.user_statistician.role, User.STATISTICIAN)
        
        # Vérification que le modèle User enregistre correctement les informations
        self.assertEqual(self.user_admin.email, 'admin@test.com')
        self.assertEqual(self.user_coach.first_name, 'Coach')
        self.assertEqual(self.user_player.last_name, 'User')
    
    def test_role_checking_methods(self):
        """
        Teste les méthodes de vérification de rôle du modèle User
        """
        # Test des méthodes is_coach, is_player, is_statistician, is_admin
        self.assertTrue(self.user_admin.is_admin())
        self.assertFalse(self.user_admin.is_coach())
        
        self.assertTrue(self.user_coach.is_coach())
        self.assertFalse(self.user_coach.is_player())
        
        self.assertTrue(self.user_player.is_player())
        self.assertFalse(self.user_player.is_statistician())
        
        self.assertTrue(self.user_statistician.is_statistician())
        self.assertFalse(self.user_statistician.is_admin())


class UserAPITests(APITestCase):
    """
    Tests pour l'API REST des utilisateurs
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests d'API
        """
        # Création des utilisateurs de test
        self.admin_user = User.objects.create_user(
            username='admin_api',
            email='admin_api@test.com',
            password='securepassword123',
            first_name='Admin',
            last_name='API',
            role=User.ADMIN
        )
        
        self.coach_user = User.objects.create_user(
            username='coach_api',
            email='coach_api@test.com',
            password='securepassword123',
            first_name='Coach',
            last_name='API',
            role=User.COACH
        )
        
        self.player_user = User.objects.create_user(
            username='player_api',
            email='player_api@test.com',
            password='securepassword123',
            first_name='Player',
            last_name='API',
            role=User.PLAYER
        )
        
        # Client API pour les tests
        self.client = APIClient()
    
    def test_user_list_admin_access(self):
        """
        Teste l'accès à la liste des utilisateurs par un administrateur
        """
        # Authentification en tant qu'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Requête à l'endpoint de liste des utilisateurs
        response = self.client.get(reverse('user-list'))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que tous les utilisateurs sont retournés
        self.assertEqual(len(response.data), User.objects.count())
    
    def test_user_list_coach_access(self):
        """
        Teste l'accès à la liste des utilisateurs par un coach
        """
        # Authentification en tant que coach
        self.client.force_authenticate(user=self.coach_user)
        
        # Requête à l'endpoint de liste des utilisateurs
        response = self.client.get(reverse('user-list'))
        
        # Vérification du statut de la réponse (devrait être 200 OK selon nos permissions)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_list_player_access(self):
        """
        Teste l'accès à la liste des utilisateurs par un joueur (devrait être refusé)
        """
        # Authentification en tant que joueur
        self.client.force_authenticate(user=self.player_user)
        
        # Requête à l'endpoint de liste des utilisateurs
        response = self.client.get(reverse('user-list'))
        
        # Vérification du statut de la réponse (devrait être 403 FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_detail_access(self):
        """
        Teste l'accès aux détails d'un utilisateur
        """
        # Authentification en tant que coach
        self.client.force_authenticate(user=self.coach_user)
        
        # Requête à l'endpoint de détail d'un utilisateur
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.player_user.pk}))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification des données retournées
        self.assertEqual(response.data['username'], self.player_user.username)
        self.assertEqual(response.data['email'], self.player_user.email)
    
    def test_user_create_admin_access(self):
        """
        Teste la création d'un utilisateur par un administrateur
        """
        # Authentification en tant qu'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Données pour le nouvel utilisateur
        new_user_data = {
            'username': 'new_user',
            'email': 'new@test.com',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.PLAYER
        }
        
        # Requête POST pour créer un nouvel utilisateur
        response = self.client.post(reverse('user-list'), new_user_data, format='json')
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérification que l'utilisateur a bien été créé en base de données
        self.assertTrue(User.objects.filter(username='new_user').exists())
    
    def test_user_create_non_admin_access(self):
        """
        Teste la création d'un utilisateur par un non-administrateur (devrait être refusée)
        """
        # Authentification en tant que coach
        self.client.force_authenticate(user=self.coach_user)
        
        # Données pour le nouvel utilisateur
        new_user_data = {
            'username': 'another_user',
            'email': 'another@test.com',
            'password': 'anotherpassword123',
            'password_confirm': 'anotherpassword123',
            'first_name': 'Another',
            'last_name': 'User',
            'role': User.PLAYER
        }
        
        # Requête POST pour créer un nouvel utilisateur
        response = self.client.post(reverse('user-list'), new_user_data, format='json')
        
        # Vérification du statut de la réponse (devrait être 403 FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Vérification que l'utilisateur n'a pas été créé en base de données
        self.assertFalse(User.objects.filter(username='another_user').exists())
    
    def test_me_endpoint(self):
        """
        Teste l'endpoint 'me' qui renvoie les informations de l'utilisateur connecté
        """
        # Authentification en tant que joueur
        self.client.force_authenticate(user=self.player_user)
        
        # Requête à l'endpoint 'me'
        response = self.client.get(reverse('user-me'))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification des données retournées
        self.assertEqual(response.data['username'], self.player_user.username)
        self.assertEqual(response.data['email'], self.player_user.email)
        self.assertEqual(response.data['role'], User.PLAYER)
    
    def test_update_me_endpoint(self):
        """
        Teste l'endpoint 'update_me' qui permet à un utilisateur de mettre à jour ses informations
        """
        # Authentification en tant que joueur
        self.client.force_authenticate(user=self.player_user)
        
        # Données à mettre à jour
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated_player@test.com'
        }
        
        # Requête PATCH pour mettre à jour les informations de l'utilisateur
        response = self.client.patch(reverse('user-update-me'), update_data, format='json')
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que les données ont été mises à jour
        self.player_user.refresh_from_db()
        self.assertEqual(self.player_user.first_name, 'Updated')
        self.assertEqual(self.player_user.last_name, 'Name')
        self.assertEqual(self.player_user.email, 'updated_player@test.com')
    
    def test_user_delete_admin_access(self):
        """
        Teste la suppression d'un utilisateur par un administrateur
        """
        # Authentification en tant qu'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Requête DELETE pour supprimer un utilisateur
        response = self.client.delete(reverse('user-detail', kwargs={'pk': self.player_user.pk}))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Vérification que l'utilisateur a bien été supprimé
        self.assertFalse(User.objects.filter(pk=self.player_user.pk).exists())
    
    def test_user_delete_non_admin_access(self):
        """
        Teste la suppression d'un utilisateur par un non-administrateur (devrait être refusée)
        """
        # Authentification en tant que coach
        self.client.force_authenticate(user=self.coach_user)
        
        # Requête DELETE pour supprimer un utilisateur
        response = self.client.delete(reverse('user-detail', kwargs={'pk': self.player_user.pk}))
        
        # Vérification du statut de la réponse (devrait être 403 FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Vérification que l'utilisateur n'a pas été supprimé
        self.assertTrue(User.objects.filter(pk=self.player_user.pk).exists())
