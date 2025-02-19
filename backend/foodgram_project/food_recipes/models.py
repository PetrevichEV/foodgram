from django.db import models
from django.urls import reverse

from django.core.validators import MinValueValidator

from django.contrib.auth import get_user_model

from .validators import validate_slug

User = get_user_model()

MIN_AMOUNT = 1


class Tag(models.Model):
    """Модель тагов."""
    name = models.CharField(
        max_length=32,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=32,
        verbose_name='Слаг',
        validators=(validate_slug,)
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель ингридиентов."""
    name = models.CharField(
        max_length=128,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientForRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='food_recipes/',
        verbose_name='Изображение'
    )

    def get_absolute_url(self):
        return f"/api/recipes/{self.pk}/"

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientForRecipe(models.Model):
    """Модель ингридиентов для рецептов."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self) -> str:
        return f'{self.recipe},{self.ingredient}'


class Favourites(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'

    def __str__(self):
        return f'{self.user},{self.recipe}'


class ShoppingList(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppings'
    )

    class Meta:
        verbose_name = 'Список покупок'

    def __str__(self):
        return f'{self.user},{self.recipe}'


class ShortLink(models.Model):
    short_id = models.CharField(max_length=8, unique=True, db_index=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.short_id} -> {self.recipe.pk}"
