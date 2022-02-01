from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from recipes.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, TagRecipe)
from users.models import User
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='unit')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        user = request.user
        is_favorited = False
        recipe = obj
        try:
            is_favorited = Favorite.objects.filter(
                user=user, recipe=recipe
            ).exists()
        except Exception:
            return is_favorited
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        user = request.user
        is_in_cart = False
        recipe = obj
        try:
            is_in_cart = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists()
        except Exception:
            return is_in_cart
        return is_in_cart

    def get_ingredients(self, obj):
        return IngredientRecipeSerializer(
            IngredientRecipe.objects.filter(recipe=obj).all(), many=True
        ).data


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='id'
    )
    ingredients = IngredientRecipeCreateSerializer(
        many=True,
        source='ingredient_recipe'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'image', 'name',
            'text', 'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(**validated_data, image=image)
        bulk_list = list()
        for elem in ingredients:
            bulk_list.append(
                IngredientRecipe(
                    ingredient=elem['id'],
                    recipe=recipe,
                    amount=elem['amount']
                )
            )
        IngredientRecipe.objects.bulk_create(bulk_list)
        for tag in tags:
            TagRecipe.objects.create(
                tag=tag, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredient_recipe')
        super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.save()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            curr_ingredient = ingredient['id']
            amount = ingredient['amount']
            IngredientRecipe.objects.update_or_create(
                ingredient=curr_ingredient, recipe=instance, amount=amount)
        return instance

    def validate(self, data):
        ingredients_data = data.get('ingredient_recipe')
        for item in ingredients_data:
            amount = item.get('amount')
            if int(amount) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0'
                )
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class FavoriteShoppingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        return FavoriteShoppingSerializer(
            Recipe.objects.filter(author=obj).all(), many=True
        ).data

    def get_recipes_count(self, obj):
        count = obj.recipes.count()
        return count


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]
