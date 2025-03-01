from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

# Création du routeur pour les ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)

# Les URLs de l'API pour l'application users
urlpatterns = [
    path('', include(router.urls)),
]
