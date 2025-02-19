from django.http import HttpResponse, HttpResponseNotFound

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.shortcuts import get_object_or_404, redirect

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from hashids import Hashids

from djoser.views import UserViewSet as DjoserUserViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import PagePaginator
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeNewSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
    UserSubscriptionSerializer,
)
from food_recipes.models import (
    Favourites,
    Ingredient,
    Recipe,
    ShoppingList,
    ShortLink,
    Tag,
)
from users.models import Subscription

hashids = Hashids(salt=settings.HASHIDS_SALT, min_length=3)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для управления текущим пользователем."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
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
        methods=['PUT', 'DELETE'],
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
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Создание и удаление подписки."""
        author = get_object_or_404(User, pk=id)
        user = request.user

        if user == author:
            return Response({"detail": "Вы не можете подписаться на себя."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            data = {'user': user.pk, 'author': author.pk}
            serializer = SubscriptionSerializer(
                data=data, context=self.get_serializer_context())
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(
                    user=user, author=author)
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response(
                    {"detail": "Вы не подписаны на этого пользователя."},
                    status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
    pagination_class = PagePaginator
    http_method_names = ('get', 'post', 'patch', 'delete')

    def _annotate_favorite(self, queryset, user):
        """Добавляем поле is_favorited."""
        return queryset.annotate(is_favorited=Exists(Favourites.objects.filter(
            user=user, recipe=OuterRef('pk'))))

    def _annotate_shopping_cart(self, queryset, user):
        """Добавляем поле is_in_shopping_cart."""
        return queryset.annotate(is_in_shopping_cart=Exists(ShoppingList.objects.filter(
            user=user, recipe=OuterRef('pk'))))

    def get_queryset(self):
        """Получаем queryset рецептов."""
        current_user = self.request.user
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'tags', 'ingredients')
        if current_user.is_authenticated:
            queryset = self._annotate_favorite(
                queryset, current_user
            )
            queryset = self._annotate_shopping_cart(
                queryset, current_user
            )
        return queryset

    def get_serializer_class(self):
        """Определение сериализатора для текущего действия."""
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeSerializer
        return RecipeNewSerializer

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        url_name='favorite',
        permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            try:
                favorite, created = Favourites.objects.get_or_create(
                    user=user, recipe=recipe)
                if created:
                    serializer = FavoriteSerializer(
                        favorite)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response({"detail": "Рецепт уже в избранном."},
                                    status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Favourites.objects.filter(
                user=user, recipe=recipe).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"detail": "Рецепт не найден в избранном."},
                                status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт из корзины покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            try:
                shopping_list, created = ShoppingList.objects.get_or_create(
                    user=user, recipe=recipe)
                if created:
                    serializer = ShoppingListSerializer(shopping_list)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response({"detail": "Рецепт уже в корзине."},
                                    status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"detail": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            deleted, _ = ShoppingList.objects.filter(
                user=user, recipe=recipe).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"detail": "Рецепт не найден в корзине."},
                                status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок для текущего пользователя."""
        user = request.user

        ingredients = ShoppingList.objects.filter(user=user).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))

        filename = f"{user.username}_shopping_list.txt"
        content = "\n".join([
            f"{item['recipe__ingredients__name']} - {item['total_amount']} "
            f"{item['recipe__ingredients__measurement_unit']}"
            for item in ingredients
        ])

        response = HttpResponse(
            content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(
        detail=True,
        methods=('GET',),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Генерирует короткую ссылку на рецепт."""
        recipe = self.get_object()
        try:
            short_link_obj = ShortLink.objects.get(recipe=recipe)
            short_id = short_link_obj.short_id
            short_link = f'{settings.BASE_URL}/api/s/{short_id}'
            return Response({'short-link': short_link})
        except ShortLink.DoesNotExist:
            short_id = hashids.encode(recipe.pk)
            short_link_obj = ShortLink.objects.create(
                short_id=short_id, recipe=recipe)
            short_link = f'{settings.BASE_URL}/api/s/{short_id}'
            return Response({'short-link': short_link})


def redirect_to_recipe(request, short_id):
    """Перенаправляет на страницу рецепта по короткой ссылке."""
    try:
        short_link_obj = ShortLink.objects.get(short_id=short_id)
        return redirect(short_link_obj.recipe.get_absolute_url())
    except ShortLink.DoesNotExist:
        return HttpResponseNotFound('Рецепт не найден')
