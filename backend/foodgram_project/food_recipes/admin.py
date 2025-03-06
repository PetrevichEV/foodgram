from django.contrib import admin
from django.db.models import Prefetch

from .models import (
    Favourite,
    Ingredient,
    IngredientForRecipe,
    Recipe,
    ShoppingList,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'tags_list',
                    'ingredients_list', 'added_favorites')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('tags', 'author__username')
    readonly_fields = ('added_favorites',)

    def get_queryset(self, request):
        """Оптимизация запросов"""
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related(
            'tags',
            Prefetch('ingredients', queryset=Ingredient.objects.all()),
        )

    def added_favorites(self, obj):
        """Подсчет общего числа добавлений рецепта в избранное."""
        return Favourite.objects.filter(recipe=obj).count()

    added_favorites.short_description = 'Всего в избранном'

    @admin.display(description='Теги')
    def tags_list(self, obj):
        """Вывод тегов"""
        return ', '.join([tags.name for tags in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, recipe):
        """Вывод ингредиентов."""
        return ', '.join([
            ingredient.name for ingredient in recipe.ingredients.all()
        ])


@admin.register(Favourite)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('user',)
    list_filter = ('recipe__name', 'user__username')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('user',)
    list_filter = ('recipe__name', 'user__username')


@admin.register(IngredientForRecipe)
class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount', )
    list_display_links = ('ingredient',)
    list_filter = ('recipe__name',)
