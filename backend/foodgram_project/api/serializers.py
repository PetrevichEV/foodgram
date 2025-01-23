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

    autor_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        """Создает подписку для текущего пользователя на пользователя."""
        subscriber = self.context['request'].user
        autor_id = validated_data['autor_id']

        if subscriber.id == autor_id:
            raise ValidationError({"Нельзя подписаться на самого себя"})

        autor = get_object_or_404(User, pk=autor_id)

        try:
            subscriptions_obj = Subscription.objects.create(
                autor=autor, subscriber=subscriber)
            return subscriptions_obj
        except IntegrityError:
            raise ValidationError({"Вы уже подписаны на этого пользователя"})

    def delete(self, validated_data):
        """Удаляет подписку для текущего пользователя."""

        subscriber = self.context['request'].user
        autor_id = validated_data['autor_id']
        autor = get_object_or_404(User, pk=autor_id)

        subscriptions_obj = Subscription.objects.filter(
            autor=autor, subscriber=subscriber).first()

        if not subscriptions_obj:
            raise ValidationError({"Подписка не найдена"})
        subscriptions_obj.delete()
        return subscriptions_obj


class SubscriptionListSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'subscriptions']


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
