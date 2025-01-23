from rest_framework import serializers
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from food_recipes.models import Recipe, Ingredient, IngredientForRecipe, Tag
from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'avatar')


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar', )

class SubscriptionNewSerializer(serializers.ModelSerializer):
    """Cоздание/удаление подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        author = instance.author
        serializer = SubscriptionListSerializer(author, context=self.context)
        return serializer.data


class SubscriptionListSerializer(UserSerializer):
    """Отображение подписанного пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes_count',
            'recipes'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    
    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj)
        return RecipeListSerializer(queryset, many=True,
                                    context=self.context).data


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
