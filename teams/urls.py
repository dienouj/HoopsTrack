from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TeamViewSet, PlayerViewSet

# Création du routeur pour les ViewSets
router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'players', PlayerViewSet)

# Les URLs de l'API pour l'application teams
urlpatterns = [
    path('', include(router.urls)),
]
