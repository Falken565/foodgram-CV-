from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import utils
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register(r'^tags', TagViewSet, basename='tags')
router.register(r'^ingredients', IngredientViewSet, basename='ingredients')
router.register(r'^recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        utils.download_shopping_cart,
        name='ownload_shopping_cart'
    ),
    path('', include(router.urls)),
]
