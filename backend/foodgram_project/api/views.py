from django.contrib.auth import get_user_model
from django.db.models import Exists, F, OuterRef, Sum
from django.http import FileResponse

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import RedirectView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse

from djoser.views import UserViewSet as DjoserUserViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import PagePaginator
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    IngredientForRecipe,
    RecipeNewSerializer,
    RecipeSerializer,
    SubscriptionListSerializer,
    SubscriptionNewSerializer,
    TagSerializer,
    UserSerializer,
    FavoriteSerializer,
    ShoppingListSerializer,
)
from food_recipes.models import (
    Favourites,
    Ingredient,
    Recipe,
    ShoppingList,
    Tag,
)
from users.models import Subscription


User = get_user_model()

FILE_NAME = 'shopping_list.txt'


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для управления текущим пользователем."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PagePaginator

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Отражение текущего пользователя."""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=('put',),
        url_path='me/avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request):
        """Добавление/обновление аватара."""
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара."""
        user = self.request.user
        if user.avatar:
            user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
            detail=False,
            methods=('GET'),
            permission_classes=(permissions.IsAuthenticated)
    )
    def subscriptions(self, request):
        """Получение списка подписок"""
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionListSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
            detail=True,
            methods=('POST'),
            permission_classes=(permissions.IsAuthenticated),
            url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        """Создание подписки."""
        user_to_follow = get_object_or_404(User, id=id)
        serializer = SubscriptionNewSerializer(
            data={'user': request.user.id, 'author': user_to_follow.id},
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def remove_subscription(self, request, id=None):
        """Удаление подписки."""
        user_to_follow = get_object_or_404(User, id=id)
        deleted_count, _ = Subscription.objects.filter(
            user=request.user, author=user_to_follow
        ).delete()
        if not deleted_count:
            return Response(
                {'detail': 'Вы не подписаны на пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """Определение сериализатора для текущего действия."""
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeSerializer
        return RecipeNewSerializer

    def _annotate_favorite(self, queryset, user):
        """Добавляем поле is_favorited."""
        return queryset.annotate(
            is_favorited=Exists(
                Favourites.objects.filter(
                    user=user,
                    recipe=OuterRef('pk')
                )
            )
        )

    def _annotate_shopping_cart(self, queryset, user):
        """Добавляем поле is_in_shopping_cart."""
        return queryset.annotate(
            is_in_shopping_cart=Exists(
                ShoppingList.objects.filter(
                    user=user,
                    recipe=OuterRef('pk')
                )
            )
        )

    def get_queryset(self):
        """Получаем queryset рецептов."""
        current_user = self.request.user
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'tags',
            'ingredients'
        )
        if current_user.is_authenticated:
            queryset = self._annotate_favorite(
                queryset, current_user
            )
            queryset = self._annotate_shopping_cart(
                queryset, current_user
            )
        return queryset

    @action(detail=True, methods=('post',),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное."""
        return self._handle_favorite_or_cart(request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = Favourites.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT if deleted
            else status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=('post',),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в корзину покупок."""
        return self._handle_favorite_or_cart(
            request, pk, ShoppingListSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из корзины покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = ShoppingList.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT if deleted
            else status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивает файл со списком покупок для текущего пользователя."""
        ingredients = (
            IngredientForRecipe.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values(
                name=F('ingredient__name'),
                unit=F('ingredient__measurement_unit')
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('name')
        )
        file_lines = [
            f'{ingredient["name"]} ({ingredient["unit"]}) — '
            f'{ingredient["total_amount"]}'
            for ingredient in ingredients
        ]

        file_content = 'Список покупок:\n' + '\n'.join(file_lines)
        response = FileResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{FILE_NAME}"'
        return response

    @action(detail=True, methods=('get',),
            url_path='get-link')
    def get_link(self, request, pk=None):
        """Генерирует короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_url_path = reverse(
            'redirect_to_original', kwargs={'slug': recipe.short_url}
        )
        short_link = request.build_absolute_uri(short_url_path)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    def _handle_favorite_or_cart(self, request, pk, serializer_class):
        """Внутренний метод для добавления рецепта в избранное или корзину."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': recipe.id},
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ShortLink(RedirectView):
    """Вьюсет для короткой ссылки."""
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Recipe, short_link=kwargs['short_link'])
        return self.request.build_absolute_uri(obj.get_absolute_url())