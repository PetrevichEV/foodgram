from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as DjoserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from food_recipes.models import (
    Favourites,
    Ingredient,
    IngredientForRecipe,
    Recipe,
    ShoppingList,
    Tag,
)
from users.models import Subscription

User = get_user_model()


class UserSerializer(DjoserSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Проверка подписки текущего пользователя на автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания модели пользователя."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        read_only_fields = ('id',)


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения аватара."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if 'avatar' not in data:
            raise serializers.ValidationError('Обязательное поле!')
        return data


class SimpleRecipeSerializer(serializers.ModelSerializer):
    """Короткое отображение информации о рецептах."""

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class UserSubscriptionSerializer(UserSerializer):
    """Сериализатор для отображение подписанного пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')

    def get_recipes_count(self, obj):
        """Подсчитывает общего количества рецептов пользователя."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Получает список рецептов автора с учетом лимита."""
        request = self.context.get('request')
        queryset = Recipe.objects.filter(author=obj)
        recipes_limit = request.query_params.get(
            'recipes_limit'
        )

        try:
            if recipes_limit and int(recipes_limit) > 0:
                queryset = queryset[:int(recipes_limit)]
        except (ValueError, TypeError):
            pass

        return SimpleRecipeSerializer(
            queryset, many=True, context=self.context
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        user, author = data['user'], data['author']

        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!'
            )

        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя!'
            )

        return data

    def to_representation(self, instance):
        """Возвращаем информацию о пользователе,
        на которого была создана подписка."""
        author = instance.author
        serializer = UserSubscriptionSerializer(author, context=self.context)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientForRecipeSerializer(
        many=True, read_only=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favourites.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingList.objects.filter(user=user, recipe=obj).exists()
        return False


class IngredientForRecipeCreateSerializer(serializers.ModelSerializer):
    """Добавление ингредиентов при создании, обновлении рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class RecipeСreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), allow_empty=False
    )
    author = UserSerializer(read_only=True,)
    ingredients = IngredientForRecipeCreateSerializer(
        many=True, allow_empty=False,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def validate(self, data):
        """Проверяет уникальность тегов и ингредиентов."""
        if not data.get('tags'):
            raise serializers.ValidationError('Укажите теги!')
        if len(set(data['tags'])) != len(data['tags']):
            raise serializers.ValidationError('Теги не уникальны!')

        if not data.get('ingredients'):
            raise serializers.ValidationError('Укажите ингредиенты!')
        ingredient_ids = [i['ingredient'].id for i in data['ingredients']]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError('Ингредиенты не уникальны!')
        return data

    def validate_image(self, img):
        """Проверяет наличие картинки рецепта."""
        if not img:
            raise serializers.ValidationError('Нужно изображение!')
        return img

    @staticmethod
    def add_ingredients(recipe, ingredients):
        """Добавляет ингредиенты в рецепт."""
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
        """Создает рецепт."""
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
        """Обновляет рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Преобразовывает объект рецепта в представление."""
        return RecipeSerializer(instance, context=self.context).data


class UserRecipeRelationMixin:
    """Валидация связи User-Recipe и сериализация в кратком виде."""

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже добавлен!')
        return data

    def to_representation(self, instance):
        """Возвращаем краткую информацию о рецептах."""
        recipe = instance.recipe
        serializer = SimpleRecipeSerializer(recipe, context=self.context)
        return serializer.data

    class Meta:
        fields = ('user', 'recipe')


class FavoriteSerializer(UserRecipeRelationMixin,
                         serializers.ModelSerializer,):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta(UserRecipeRelationMixin.Meta):
        model = Favourites


class ShoppingListSerializer(UserRecipeRelationMixin,
                             serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в корзину покупок."""

    class Meta(UserRecipeRelationMixin.Meta):
        model = ShoppingList
