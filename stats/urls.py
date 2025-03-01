from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GameViewSet, PerformanceViewSet, TeamPerformanceViewSet

# Création du routeur pour les ViewSets
router = DefaultRouter()
router.register(r'games', GameViewSet)
router.register(r'performances', PerformanceViewSet)
router.register(r'team-performances', TeamPerformanceViewSet)

# Les URLs de l'API pour l'application stats
urlpatterns = [
    path('', include(router.urls)),
]
