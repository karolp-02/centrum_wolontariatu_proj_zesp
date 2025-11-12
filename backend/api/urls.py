from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.ProjektViewSet, basename='projects')
router.register(r'offers', views.OfertaViewSet, basename='offers')

urlpatterns = [
    path('', include(router.urls)),
]
