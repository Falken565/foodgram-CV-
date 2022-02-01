from django.contrib import admin
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.html import format_html

from users.models import User

from .validators import cooking_time_amount_validator


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    REQUIRED_FIELDS = ['name', 'unit']

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return '{}, {}'.format(self.name, self.unit)


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(
        unique=True,
        max_length=200,
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            ('Имя может содержать латинские буквы и цифры')
        )]
    )

    REQUIRED_FIELDS = ['name', 'color', 'slug']

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    @admin.display
    def colored_name(self):
        return format_html('<span style="color: {};">{}</span>',
                           self.color,
                           self.name)


class Recipe(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[cooking_time_amount_validator]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name='Картинка'
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        null=True,
        blank=True
    )

    REQUIRED_FIELDS = [
        'name', 'text', 'cooking_time',
        'ingredients', 'tags', 'image', 'author'
    ]

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_recipe',
        on_delete=CASCADE)
    amount = models.IntegerField(
        verbose_name='Количество',
        # validators=[validate_amount],
    )

    REQUIRED_FIELDS = ['ingredient', 'recipe', 'amount']

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return '{}, {}'.format(self.ingredient, self.amount)


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=CASCADE)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following")

    def __str__(self):
        return '{} - {}'.format(self.user, self.author)


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="favorite")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite recipe'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="customer")
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="purchase")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='recipe in cart'
            )
        ]
