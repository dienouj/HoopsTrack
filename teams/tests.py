from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from .models import Team, Player
from .serializers import TeamSerializer, PlayerSerializer
from datetime import date

class TeamModelTests(TestCase):
    """
    Tests pour le modèle Team
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests
        """
        # Création des utilisateurs pour les tests
        self.coach_user = User.objects.create_user(
            username='coach_team',
            email='coach_team@test.com',
            password='securepassword123',
            first_name='Coach',
            last_name='Team',
            role=User.COACH
        )
        
        self.statistician_user = User.objects.create_user(
            username='stat_team',
            email='stat_team@test.com',
            password='securepassword123',
            first_name='Stat',
            last_name='Team',
            role=User.STATISTICIAN
        )
        
        # Création d'une équipe pour les tests
        self.team = Team.objects.create(
            name='Test Team',
            city='Test City',
            coach=self.coach_user,
            description='A test team'
        )
        
        # Ajout d'un statisticien à l'équipe
        self.team.staff.add(self.statistician_user)
    
    def test_team_creation(self):
        """
        Teste la création d'une équipe
        """
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(self.team.city, 'Test City')
        self.assertEqual(self.team.coach, self.coach_user)
        self.assertTrue(self.statistician_user in self.team.staff.all())
    
    def test_team_string_representation(self):
        """
        Teste la représentation en chaîne du modèle Team
        """
        self.assertEqual(str(self.team), 'Test Team')


class PlayerModelTests(TestCase):
    """
    Tests pour le modèle Player
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests
        """
        # Création des utilisateurs pour les tests
        self.coach_user = User.objects.create_user(
            username='coach_player',
            email='coach_player@test.com',
            password='securepassword123',
            first_name='Coach',
            last_name='Player',
            role=User.COACH
        )
        
        self.player_user = User.objects.create_user(
            username='player_model',
            email='player_model@test.com',
            password='securepassword123',
            first_name='Player',
            last_name='Model',
            role=User.PLAYER
        )
        
        # Création d'une équipe pour les tests
        self.team = Team.objects.create(
            name='Player Test Team',
            city='Test City',
            coach=self.coach_user
        )
        
        # Création d'un joueur pour les tests
        self.player = Player.objects.create(
            user=self.player_user,
            team=self.team,
            jersey_number=23,
            position='SG',
            height=198,
            weight=98,
            birth_date=date(1998, 5, 15)
        )
    
    def test_player_creation(self):
        """
        Teste la création d'un joueur
        """
        self.assertEqual(self.player.user, self.player_user)
        self.assertEqual(self.player.team, self.team)
        self.assertEqual(self.player.jersey_number, 23)
        self.assertEqual(self.player.position, 'SG')
        self.assertEqual(self.player.height, 198)
        self.assertEqual(self.player.weight, 98)
        self.assertEqual(self.player.birth_date, date(1998, 5, 15))
        self.assertTrue(self.player.active)  # Par défaut, un joueur est actif
    
    def test_player_string_representation(self):
        """
        Teste la représentation en chaîne du modèle Player
        """
        expected_repr = f"{self.player_user.first_name} {self.player_user.last_name} (#{self.player.jersey_number})"
        self.assertEqual(str(self.player), expected_repr)


class TeamAPITests(APITestCase):
    """
    Tests pour l'API REST des équipes
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests d'API
        """
        # Création des utilisateurs pour les tests
        self.admin_user = User.objects.create_user(
            username='admin_team_api',
            email='admin_team@test.com',
            password='securepassword123',
            first_name='Admin',
            last_name='Team',
            role=User.ADMIN
        )
        
        self.coach_user = User.objects.create_user(
            username='coach_team_api',
            email='coach_team_api@test.com',
            password='securepassword123',
            first_name='Coach',
            last_name='Team',
            role=User.COACH
        )
        
        self.player_user = User.objects.create_user(
            username='player_team_api',
            email='player_team_api@test.com',
            password='securepassword123',
            first_name='Player',
            last_name='Team',
            role=User.PLAYER
        )
        
        # Création d'équipes pour les tests
        self.team1 = Team.objects.create(
            name='API Test Team 1',
            city='API City 1',
            coach=self.coach_user,
            description='First test team for API'
        )
        
        self.team2 = Team.objects.create(
            name='API Test Team 2',
            city='API City 2',
            description='Second test team for API'
        )
        
        # Création d'un joueur pour les tests
        self.player = Player.objects.create(
            user=self.player_user,
            team=self.team1,
            jersey_number=10,
            position='PG'
        )
        
        # Client API pour les tests
        self.client = APIClient()
    
    def test_team_list(self):
        """
        Teste l'accès à la liste des équipes
        """
        # Authentification
        self.client.force_authenticate(user=self.player_user)
        
        # Requête à l'endpoint de liste des équipes
        response = self.client.get(reverse('team-list'))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que toutes les équipes sont retournées
        self.assertEqual(len(response.data), Team.objects.count())
    
    def test_team_detail(self):
        """
        Teste l'accès aux détails d'une équipe
        """
        # Authentification
        self.client.force_authenticate(user=self.player_user)
        
        # Requête à l'endpoint de détail d'une équipe
        response = self.client.get(reverse('team-detail', kwargs={'pk': self.team1.pk}))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification des données retournées
        self.assertEqual(response.data['name'], self.team1.name)
        self.assertEqual(response.data['city'], self.team1.city)
    
    def test_team_create(self):
        """
        Teste la création d'une équipe
        """
        # Authentification en tant qu'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Données pour la nouvelle équipe
        new_team_data = {
            'name': 'New API Team',
            'city': 'New City',
            'description': 'A new team created via API'
        }
        
        # Requête POST pour créer une nouvelle équipe
        response = self.client.post(reverse('team-list'), new_team_data, format='json')
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérification que l'équipe a bien été créée en base de données
        self.assertTrue(Team.objects.filter(name='New API Team').exists())
    
    def test_team_update(self):
        """
        Teste la mise à jour d'une équipe
        """
        # Authentification en tant que coach de l'équipe
        self.client.force_authenticate(user=self.coach_user)
        
        # Données pour la mise à jour
        update_data = {
            'description': 'Updated team description'
        }
        
        # Requête PATCH pour mettre à jour partiellement l'équipe
        response = self.client.patch(
            reverse('team-detail', kwargs={'pk': self.team1.pk}),
            update_data,
            format='json'
        )
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que les données ont été mises à jour
        self.team1.refresh_from_db()
        self.assertEqual(self.team1.description, 'Updated team description')
    
    def test_team_players_endpoint(self):
        """
        Teste l'endpoint personnalisé pour récupérer les joueurs d'une équipe
        """
        # Authentification
        self.client.force_authenticate(user=self.player_user)
        
        # Requête à l'endpoint personnalisé
        response = self.client.get(reverse('team-players', kwargs={'pk': self.team1.pk}))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que le joueur créé est bien retourné
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.player_user.id)
        self.assertEqual(response.data[0]['jersey_number'], 10)


class PlayerAPITests(APITestCase):
    """
    Tests pour l'API REST des joueurs
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests d'API
        """
        # Création des utilisateurs pour les tests
        self.coach_user = User.objects.create_user(
            username='coach_player_api',
            email='coach_player_api@test.com',
            password='securepassword123',
            first_name='Coach',
            last_name='Player',
            role=User.COACH
        )
        
        self.player_user1 = User.objects.create_user(
            username='player_api_1',
            email='player_api_1@test.com',
            password='securepassword123',
            first_name='Player1',
            last_name='API',
            role=User.PLAYER
        )
        
        self.player_user2 = User.objects.create_user(
            username='player_api_2',
            email='player_api_2@test.com',
            password='securepassword123',
            first_name='Player2',
            last_name='API',
            role=User.PLAYER
        )
        
        # Création d'une équipe pour les tests
        self.team = Team.objects.create(
            name='Player API Test Team',
            city='API City',
            coach=self.coach_user
        )
        
        # Création de joueurs pour les tests
        self.player1 = Player.objects.create(
            user=self.player_user1,
            team=self.team,
            jersey_number=5,
            position='PG',
            height=185,
            weight=80
        )
        
        self.player2 = Player.objects.create(
            user=self.player_user2,
            team=self.team,
            jersey_number=7,
            position='SG',
            height=195,
            weight=90,
            active=False
        )
        
        # Client API pour les tests
        self.client = APIClient()
    
    def test_player_list(self):
        """
        Teste l'accès à la liste des joueurs
        """
        # Authentification
        self.client.force_authenticate(user=self.coach_user)
        
        # Requête à l'endpoint de liste des joueurs
        response = self.client.get(reverse('player-list'))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que tous les joueurs sont retournés
        self.assertEqual(len(response.data), Player.objects.count())
    
    def test_player_detail(self):
        """
        Teste l'accès aux détails d'un joueur
        """
        # Authentification
        self.client.force_authenticate(user=self.player_user1)
        
        # Requête à l'endpoint de détail d'un joueur
        response = self.client.get(reverse('player-detail', kwargs={'pk': self.player1.pk}))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification des données retournées
        self.assertEqual(response.data['user'], self.player_user1.id)
        self.assertEqual(response.data['user_first_name'], self.player_user1.first_name)
        self.assertEqual(response.data['user_last_name'], self.player_user1.last_name)
        self.assertEqual(response.data['jersey_number'], 5)
        self.assertEqual(response.data['position'], 'PG')
    
    def test_player_create(self):
        """
        Teste la création d'un joueur
        """
        # Création d'un nouvel utilisateur pour le test
        new_user = User.objects.create_user(
            username='new_player',
            email='new_player@test.com',
            password='securepassword123',
            first_name='New',
            last_name='Player',
            role=User.PLAYER
        )
        
        # Authentification en tant que coach
        self.client.force_authenticate(user=self.coach_user)
        
        # Données pour le nouveau joueur
        new_player_data = {
            'user': new_user.id,
            'team': self.team.id,
            'jersey_number': 15,
            'position': 'C',
            'height': 210,
            'weight': 110
        }
        
        # Requête POST pour créer un nouveau joueur
        response = self.client.post(reverse('player-list'), new_player_data, format='json')
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérification que le joueur a bien été créé en base de données
        self.assertTrue(Player.objects.filter(user=new_user).exists())
        
        # Récupération du joueur créé
        created_player = Player.objects.get(user=new_user)
        self.assertEqual(created_player.jersey_number, 15)
        self.assertEqual(created_player.position, 'C')
    
    def test_player_update(self):
        """
        Teste la mise à jour d'un joueur
        """
        # Authentification en tant que coach
        self.client.force_authenticate(user=self.coach_user)
        
        # Données pour la mise à jour
        update_data = {
            'jersey_number': 99,
            'position': 'SF'
        }
        
        # Requête PATCH pour mettre à jour partiellement le joueur
        response = self.client.patch(
            reverse('player-detail', kwargs={'pk': self.player1.pk}),
            update_data,
            format='json'
        )
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que les données ont été mises à jour
        self.player1.refresh_from_db()
        self.assertEqual(self.player1.jersey_number, 99)
        self.assertEqual(self.player1.position, 'SF')
    
    def test_by_team_endpoint(self):
        """
        Teste l'endpoint personnalisé pour récupérer les joueurs par équipe
        """
        # Authentification
        self.client.force_authenticate(user=self.coach_user)
        
        # Requête à l'endpoint personnalisé
        response = self.client.get(f"{reverse('player-by-team')}?team_id={self.team.id}")
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification que les deux joueurs de l'équipe sont retournés
        self.assertEqual(len(response.data), 2)
    
    def test_by_user_endpoint(self):
        """
        Teste l'endpoint personnalisé pour récupérer le profil joueur de l'utilisateur connecté
        """
        # Authentification en tant que joueur
        self.client.force_authenticate(user=self.player_user1)
        
        # Requête à l'endpoint personnalisé
        response = self.client.get(reverse('player-me'))
        
        # Vérification du statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification des données retournées
        self.assertEqual(response.data['user'], self.player_user1.id)
        self.assertEqual(response.data['jersey_number'], 5)
