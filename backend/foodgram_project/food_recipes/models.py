import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_slug

User = get_user_model()


class Tag(models.Model):
    """Определение модели тегов."""

    name = models.CharField(
        max_length=settings.TAG_MAX_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.TAG_MAX_LENGTH,
        verbose_name='Слаг',
        validators=(validate_slug,)
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Определение модели ингридиентов."""

    name = models.CharField(
        max_length=settings.NAME_INGREDIENT_MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=settings.MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Определение модели рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=settings.NAME_RECIPE_MAX_LENGTH,
        verbose_name='Название'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(settings.MIN_TIME),
                    MaxValueValidator(settings.MAX_TIME)],
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientForRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='food_recipes/',
        verbose_name='Изображение'
    )
    short_id = models.CharField(
        max_length=settings.SHORT_ID_MAX_LENGTH,
        unique=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pk']

    def __str__(self):
        return self.name

    def generate_short_id(self):
        characters = f'{string.ascii_letters}{string.digits}'
        return ''.join(random.choices(characters,
                                      k=settings.SHORT_ID_MAX_LENGTH))

    def save(self, *args, **kwargs):
        """Переопределение метода save для создания короткой ссылки."""
        if not self.short_id:
            self.short_id = self.generate_short_id()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/recipes/{self.pk}'


class IngredientForRecipe(models.Model):
    """Определение промежуточной модели ингридиентов для рецептов."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(settings.MIN_AMOUNT),
                    MaxValueValidator(settings.MAX_AMOUNT)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        ordering = ('ingredient',)

    def __str__(self) -> str:
        return f'{self.recipe},{self.ingredient}'


class Favourite(models.Model):
    """Определение модели избранного."""

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
        verbose_name_plural = 'Избранное'
        ordering = ('user',)

    def __str__(self):
        return f'{self.user},{self.recipe}'


class ShoppingList(models.Model):
    """Определение модели списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('user',)

    def __str__(self):
        return f'{self.user},{self.recipe}'
