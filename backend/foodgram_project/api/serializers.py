from rest_framework import serializers


from food_recipes.models import Recipe, Ingredient, IngredientForRecipe


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientForRecipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'
