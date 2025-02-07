from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from drf_base64.fields import Base64ImageField

from food_recipes.models import (
    Ingredient,
    IngredientForRecipe,
    Recipe,
    Tag,
    Favourites,
    ShoppingList,
)
from users.models import Subscription


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
                ).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionNewSerializer(serializers.ModelSerializer):
    """Cозданиее подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        user, author = data['user'], data['author']

        if user == author:
            raise serializers.ValidationError(
                "Вы не можете подписаться на себя."
                )

        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на данного пользователя."
                )

        return data

    def to_representation(self, instance):
        """Возвращаем информацию о пользователе,
        на которого была создана подписка."""
        return SubscriptionListSerializer(
            instance.author,
            context=self.context
            ).data


class SubscriptionListSerializer(UserSerializer):
    """Отображение подписанного пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')

    def get_recipes_count(self, obj):
        """Подсчет общего количества рецептов пользователя."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Получение списка рецептов автора с учетом лимита."""
        queryset = Recipe.objects.filter(author=obj)
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
            )

        try:
            if recipes_limit and int(recipes_limit) > 0:
                queryset = queryset[:int(recipes_limit)]
        except (ValueError, TypeError):
            pass

        return RecipeSerializer(queryset, many=True, context=self.context).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientForRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    def to_representation(self, instance):
        recipe = instance.recipe
        serializer = RecipeSerializer(
            recipe, context=self.context
        )
        return serializer.data

    class Meta:
        model = Favourites
        fields = ('user', 'recipe')


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    def to_representation(self, instance):
        recipe = instance.recipe
        serializer = RecipeSerializer(
            recipe, context=self.context
        )
        return serializer.data

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')


class RecipeSerializer(serializers.ModelSerializer):
    """Отображение рецептов."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientForRecipeSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(
        read_only=True,
        default=0
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=0
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeNewSerializer(serializers.ModelSerializer):
    """Создание рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        allow_empty=False,
        label="Теги",
    )
    author = UserSerializer(
        read_only=True,
        label="Автор"
    )
    ingredients = IngredientForRecipeCreateSerializer(
        many=True,
        allow_empty=False,
        label="Ингредиенты",
    )
    image = Base64ImageField(label="Изображение")

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        )

    def add_ingredients(recipe, ingredients):
        """Добавление ингредиентов в рецепт."""
        ingredient_for_recipes = [
            IngredientForRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        IngredientForRecipe.objects.bulk_create(
            ingredient_for_recipes
        )

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        current_user = self.context['request'].user
        recipe = Recipe.objects.create(
            author=current_user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Преобразование объекта рецепта в представление."""
        return RecipeSerializer(
            instance,
            context=self.context
        ).data
