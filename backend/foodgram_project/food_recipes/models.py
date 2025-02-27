
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from hashids import Hashids

from .validators import validate_slug

User = get_user_model()

hashids = Hashids(salt=settings.HASHIDS_SALT, min_length=3)

class Tag(models.Model):
    """Модель тегов."""
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

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов."""
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
        max_length=settings.NAME_RECIPE_MAX_LENGTH,
        verbose_name='Название'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(settings.MIN_AMOUNT)],
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
        return f"/recipes/{self.pk}"

    def save(self, *args, **kwargs):
        """Переопределение метода save для создания короткой ссылки."""
        is_new = not self.pk  # Проверяем, является ли объект новым
        super().save(*args, **kwargs)  # Сначала сохраняем объект

        if is_new:  # Если это новый объект
            from .models import ShortLink  # Импортируем локально, чтобы избежать циклического импорта

            short_id = hashids.encode(self.pk)  # Генерируем короткий ID
            ShortLink.objects.create(short_id=short_id, recipe=self)  

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
        validators=[MinValueValidator(settings.MIN_AMOUNT)],
    )

    class Meta:
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
        related_name='shopping_list'
    )

    class Meta:
        verbose_name = 'Список покупок'

    def __str__(self):
        return f'{self.user},{self.recipe}'


class ShortLink(models.Model):
    """Модель короткой ссылки."""
    short_id = models.CharField(
        max_length=settings.SHORT_ID_MAX_LENGTH,
        unique=True,
        db_index=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return f"{self.short_id} -> {self.recipe.pk}"
