from rest_framework import serializers
from djoser.serializers import UserSerializer as DjoserUserSerializer


from food_recipes.models import Recipe, Ingredient, IngredientForRecipe, Tag
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('avatar', )

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientForRecipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'
