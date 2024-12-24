from rest_framework import serializers

# from food_recipes.models import (
#     Tag, Ingredient, Recipe, Favourites, ShoppingList)
# from users.models import User, Follow

from food_recipes.models import Recipe, Ingredient, IngredientForRecipe


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    ingredients = IngredientForRecipeSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
