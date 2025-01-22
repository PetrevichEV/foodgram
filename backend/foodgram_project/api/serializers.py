from rest_framework import serializers

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


class SubscriptionSerializer(serializers.ModelSerializer):

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


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'
