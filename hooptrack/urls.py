"""
URL configuration for hooptrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuration de Swagger/OpenAPI pour la documentation de l'API
schema_view = get_schema_view(
    openapi.Info(
        title="HoopTrack API",
        default_version='v1',
        description="API pour l'application de statistiques de basketball HoopTrack",
        terms_of_service="https://www.hooptrack.com/terms/",
        contact=openapi.Contact(email="contact@hooptrack.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),
    
    # URLs des API REST pour chaque application
    path('api/v1/auth/', include('rest_framework.urls')),  # Authentification DRF
    path('api/v1/', include('users.urls')),               # API utilisateurs
    path('api/v1/', include('teams.urls')),               # API équipes et joueurs
    path('api/v1/', include('stats.urls')),               # API statistiques
    
    # Documentation de l'API (Swagger)
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
