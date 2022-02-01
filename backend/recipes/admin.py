from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, TagRecipeInline)
    list_display = ('author', 'name', 'pub_date', 'favorite_score', 'id', )
    list_filter = ('author', 'tags', 'name',)
    empty_value_display = '-пусто-'

    @admin.display(description='added to favorite')
    def favorite_score(self, obj):
        recipe = obj
        score = Favorite.objects.filter(recipe=recipe).count()
        return score


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', )
    empty_value_display = '-пусто-'
    list_filter = ('name', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'slug', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', )
    empty_value_display = '-пусто-'


class FollowRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagRecipe)
admin.site.register(Follow, FollowRecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
