import django_filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    name = django_filters.CharFilter(field_name='author')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
