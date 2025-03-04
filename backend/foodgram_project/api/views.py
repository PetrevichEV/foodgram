import io

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from food_recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    ShoppingList,
    Tag)
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .pagination import PagePaginator
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeСreateUpdateSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
    UserSubscriptionSerializer,
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Отображение информации о пользователе."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PagePaginator

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Отражение текущего пользователя."""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=('PUT', 'DELETE'),
        url_path='me/avatar',
        url_name='avatar',
        permission_classes=[permissions.IsAuthenticated],
    )
    def avatar(self, request):
        """Добавление и обновление и удаление аватара."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('GET',),
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        queryset = User.objects.filter(
            subscribers__user=request.user
        ).annotate(recipes_count=Count('recipes')).order_by('username')
        page = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Создание и удаление подписки."""
        user = request.user

        if request.method == 'POST':
            author = get_object_or_404(User, pk=id)
            data = {'user': user.pk, 'author': author.pk}
            serializer = SubscriptionSerializer(
                data=data, context=self.get_serializer_context())
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription, _ = Subscription.objects.filter(
                user=user, author=self.get_object()
            ).delete()
            if subscription == 0:
                return Response(
                    {'detail': 'Вы не подписаны на этого пользователя!'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображение рецептов."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'recipe_ingredients__ingredient', 'tags'
    )
    # serializer_class = RecipeСreateUpdateSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PagePaginator
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeСreateUpdateSerializer

    def add_delete_recipe(self, request, model=None,
                          serializer_class=None, pk=None):
        """Механика добавления/удаления рецепта из избранного/корзины."""

        user = request.user

        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            data = {'user': user.pk, 'recipe': recipe.pk}
            serializer = serializer_class(
                data=data, context=self.get_serializer_context())
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted_count, _ = model.objects.filter(
                user=user, recipe=self.get_object()
            ).delete()

            if deleted_count == 0:
                return Response(
                    {'detail': 'Рецепт не найден!'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        url_name='favorite',
        permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Вызов функуции по добавлению/удалению рецепта из избранного."""
        return self.add_delete_recipe(
            request, Favourite, FavoriteSerializer, pk
        )

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Вызов функции по добавлению/удалению рецепта из корзины покупок."""
        return self.add_delete_recipe(
            request, ShoppingList, ShoppingListSerializer, pk
        )

    def _create_shopping_list_content(self, user):
        """Создает списк покупок."""
        buffer = io.BytesIO()
        ingredients = ShoppingList.objects.filter(user=user).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))

        content = '\n'.join([
            f"{item['recipe__ingredients__name']} - {item['total_amount']} "
            f"{item['recipe__ingredients__measurement_unit']}"
            for item in ingredients
        ])

        buffer.write(content.encode('utf-8'))

        buffer.seek(0)
        return buffer

    @action(
        detail=False,
        methods=('GET',),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание списока покупок для текущего пользователя."""
        user = request.user
        buffer = self._create_shopping_list_content(user)

        filename = f"{user.username}_shopping_list.txt"
        response = HttpResponse(
            buffer.getvalue(),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(
        detail=True,
        methods=('GET',),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Отображение короткой ссылки на рецепт."""
        recipe = self.get_object()
        short_link = f'{settings.BASE_URL}/api/s/{recipe.short_id}'
        return Response({'short-link': short_link})


def redirect_to_recipe(request, short_id):
    """Переправление на страницу рецепта по короткой ссылке."""
    recipe = get_object_or_404(Recipe, short_id=short_id)
    return redirect(recipe.get_absolute_url())
