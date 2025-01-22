from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import (RecipeListSerializer, IngredientSerializer,
                          TagSerializer, UserSerializer, AvatarSerializer,
                          SubscriptionNewSerializer,
                          SubscriptionListSerializer)
from food_recipes.models import Recipe, Ingredient, Tag
from users.models import Subscription
from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import AllowAny
from djoser.serializers import SetPasswordSerializer
from .permissions import IsOwnerOrReadOnly

from django.contrib.auth import get_user_model


User = get_user_model()


class MeUserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        """Отражение текущего пользователя."""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=('put',), url_path='me/avatar',
            permission_classes=(permissions.IsAuthenticated,))
    def avatar(self, request):
        """Добавление/обновление аватара."""
        serializer = AvatarSerializer(request.user,
                                      data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара."""
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionListViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = SubscriptionListSerializer

    def get_queryset(self):
        user = self.request.user
        return user.subscribers.filter(user=user)


class SubscriptionViewSet(viewsets.ModelViewSet):
    def post(self, request, pk):
        author = request.user
        subscriber = get_object_or_404(User, id=pk)
        create_subscriber = Subscription.objects.create(
            author=author, subscriber=subscriber)
        serializer = SubscriptionNewSerializer(
            create_subscriber, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def delete(self, request, id=None, **kwargs):
    #     return self.destroy_object(
    #         get_object_or_404(User, pk=id), self.request.user.subscriptions
    #     )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    pass


class UserViewSet(viewsets.ModelViewSet):
    pass


class FavouritesViewSet(viewsets.ModelViewSet):
    pass
