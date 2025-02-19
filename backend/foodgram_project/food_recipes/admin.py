from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, Favourites,
                     ShoppingList, IngredientForRecipe, ShortLink,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(IngredientForRecipe)
class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount',)


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_id', 'recipe',)
