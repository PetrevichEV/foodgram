from rest_framework import serializers
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField

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


class SubscriptionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('author', 'subscriber')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'subscriber'),
                message='Вы уже подписаны на данного автора!',
            ),
        )

    def validate(self, data):
        if self.context['request'].user == data['subscriber']:
            raise serializers.ValidationError(
                'Вы не можете подписаться сам на себя!'
            )
        return data

class SubscriptionNewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('author', 'subscriber')
    #     validators = (
    #         serializers.UniqueTogetherValidator(
    #             queryset=Subscription.objects.all(),
    #             fields=('author', 'subscriber'),
    #             message='Вы уже подписаны на данного автора!',
    #         ),
    #     )

    # def validate(self, data):
    #     if self.context['request'].user == data['subscriber']:
    #         raise serializers.ValidationError(
    #             'Вы не можете подписаться сам на себя!'
    #         )
    #     return data

class SubscriptionListSerializer(UserSerializer):
    email = serializers.ReadOnlyField(source='user.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'avatar',
                  'recipes_count', 'recipes', )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(user=user, following=obj.id).exists()

    def get_recipes(self, obj):
        page_size = 3
        recipes = Recipe.objects.filter(author=obj.following)
        paginator = Paginator(recipes, page_size)
        recipes_paginated = paginator.page(1)
        serializer = RecipeListSerializer(recipes_paginated, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

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
