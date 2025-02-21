from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, Favourites,
                     ShoppingList, IngredientForRecipe, ShortLink)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'tags_list', 'added_favorites')

    search_fields = ('author', 'name')
    list_filter = ('tags',)
    readonly_fields = ('added_favorites',)

    def added_favorites(self, obj):
        """Подсчет общего числа добавлений рецепта в избранное."""
        return Favourites.objects.filter(recipe=obj).count()

    added_favorites.short_description = 'Всего в избранном'

    @admin.display(description='Теги')
    def tags_list(self, obj):
        return ', '.join([tags.name for tags in obj.tags.all()])

@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(IngredientForRecipe)
class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount')


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_id', 'recipe')
