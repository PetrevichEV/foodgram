import io
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action

from rest_framework.response import Response

from food_recipes.models import (
    Favourites,
    Ingredient,
    Recipe,
    ShoppingList,
    ShortLink,
    Tag,
)
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .pagination import PagePaginator
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeСreateUpdateSerializer,
    ShoppingListSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
    UserSubscriptionSerializer,
)


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет пользователя."""

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
        """Добавление/обновление и удаление аватара."""
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
            if user == author:
                return Response({'detail': 'Нельзя подписаться на себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
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
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.prefetch_related(
        'recipe_ingredients__ingredient', 'tags', 'author'
    )
    serializer_class = RecipeСreateUpdateSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PagePaginator
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        url_name='favorite',
        permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта из избранного."""
        user = request.user

        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if Favourites.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в избранном!'},
                                status=status.HTTP_400_BAD_REQUEST)

            favorite = Favourites.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted_count, _ = Favourites.objects.filter(
                user=user, recipe=self.get_object()
            ).delete()

            if deleted_count == 0:
                return Response(
                    {'detail': 'Рецепт не найден в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта из корзины покупок."""
        user = request.user

        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в корзине!'},
                                status=status.HTTP_400_BAD_REQUEST)

            shopping_list = ShoppingList.objects.create(
                user=user, recipe=recipe
            )
            serializer = ShoppingListSerializer(shopping_list)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted_count, _ = ShoppingList.objects.filter(
                user=user, recipe=self.get_object()
            ).delete()

            if deleted_count == 0:
                return Response(
                    {'detail': 'Рецепт не найден в корзине!'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create_shopping_list_content(self, user):
        """Создает списк покупок."""
        buffer = io.BytesIO()
        ingredients = ShoppingList.objects.filter(user=user).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))

        content = "\n".join([
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
        try:
            short_link_obj = ShortLink.objects.get(recipe=recipe)
            short_id = short_link_obj.short_id
            short_link = f'{settings.BASE_URL}/api/s/{short_id}'
            return Response({'short-link': short_link})

        except ShortLink.DoesNotExist:
            return Response(
                {'detail': 'Ссылка не найдена!'},
                status=status.HTTP_404_NOT_FOUND
            )


def redirect_to_recipe(request, short_id):
    """Переправление на страницу рецепта по короткой ссылке."""
    try:
        short_link_obj = ShortLink.objects.get(short_id=short_id)
        return redirect(short_link_obj.recipe.get_absolute_url())
    except ShortLink.DoesNotExist:
        return HttpResponseNotFound('Рецепт не найден!')
