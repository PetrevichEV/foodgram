from django.contrib import admin

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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'tags_list', 'added_favorites')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    readonly_fields = ('added_favorites',)

    def added_favorites(self, obj):
        """Подсчет общего числа добавлений рецепта в избранное."""
        return Favourite.objects.filter(recipe=obj).count()

    added_favorites.short_description = 'Всего в избранном'

    @admin.display(description='Теги')
    def tags_list(self, obj):
        return ', '.join([tags.name for tags in obj.tags.all()])


@admin.register(Favourite)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(IngredientForRecipe)
class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount')
