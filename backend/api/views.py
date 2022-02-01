from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators, status, viewsets
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthor
from .serializers import (FavoriteSerializer, FavoriteShoppingSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_field = 'id'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_anonymous:
            if self.request.query_params.get('is_favorited'):
                qs = qs.filter(favorite__user=user)
            if self.request.query_params.get('is_in_shopping_cart'):
                qs = qs.filter(purchase__user=user)
            return qs
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeListSerializer
        return RecipeSerializer

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if instance.author == user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={"errors": "удалять рецепт может только автор"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @decorators.action(
        ['GET', 'DELETE'],
        detail=False,
        url_path=r'(?P<recipe_id>\d+)/favorite',
        permission_classes=[IsAuthor, ]
    )
    def favorite(self, request, *args, **kwargs):
        user = request.user
        user_pk = user.id
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if request.method == 'GET':
            serializer_val = FavoriteSerializer(
                data={'user': user_pk, 'recipe': recipe_id})
            serializer_val.is_valid(raise_exception=True)
            serializer_val.save()
            serializer = FavoriteShoppingSerializer(recipe)
            return Response(serializer.data)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={"errors": "No recipe in favorite"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @decorators.action(
        ['GET', 'DELETE'],
        detail=False,
        url_path=r'(?P<recipe_id>\d+)/shopping_cart',
        permission_classes=[IsAuthor, ])
    def shopping_cart(self, request, *args, **kwargs):
        user = request.user
        user_pk = user.id
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if request.method == 'GET':
            serializer_val = ShoppingCartSerializer(
                data={'user': user_pk, 'recipe': recipe_id})
            serializer_val.is_valid(raise_exception=True)
            serializer_val.save()
            serializer = FavoriteShoppingSerializer(recipe)
            return Response(serializer.data)
        shop_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if shop_cart.exists():
            shop_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={"errors": "No recipe in shopping cart"},
            status=status.HTTP_400_BAD_REQUEST,
        )
